from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
import json
import re
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

load_dotenv()

from app.crud.crud_user import get_doctor_specialties
from app.models.clinic import DoctorMedicalCenter, MedicalCenter, Schedule
from app.models.user import Doctor
from app.models.appointment import Appointment  # Ensure loaded for SQLAlchemy registry

async def extract_search_preferences(message: str) -> dict:
    """
    Extracts doctor preferences (specialty, clinic, day of week, doctor name) from user message.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.0
    )
    
    prompt = f"""
    Analiza el mensaje del usuario y extrae sus preferencias de agendamiento de citas médicas o búsqueda de doctores.
    Debes mapear los días de la semana a números enteros:
    - lunes: 0
    - martes: 1
    - miércoles: 2
    - jueves: 3
    - viernes: 4
    - sábado: 5
    - domingo: 6

    Responde ESTRICTAMENTE con un formato JSON (sin bloques de código markdown, sin explicaciones, solo el texto JSON puro).
    Si un parámetro no es mencionado o implícito en el mensaje, pon null.
    
    Campos a extraer:
    - specialty: Especialidad médica (ej. Cardiología, Pediatría, Medicina General, Psiquiatría, etc.)
    - clinic: Nombre de la clínica o centro médico (ej. Clínica del Sur, Clínica Alemana, etc.)
    - day_of_week: Número entero del 0 al 6 según el día de la semana mencionado
    - doctor_name: Nombre o apellido del doctor específico buscado (ej. Alejandro Perez, Dr. Perez)

    Mensaje del usuario: "{message}"
    """
    
    try:
        response = await llm.ainvoke(prompt)
        text = response.content.strip()
        
        # Clean up code blocks if present
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
            
        data = json.loads(text)
        return {
            "specialty": data.get("specialty"),
            "clinic": data.get("clinic"),
            "day_of_week": data.get("day_of_week"),
            "doctor_name": data.get("doctor_name")
        }
    except Exception as e:
        print(f"Error extracting search preferences: {e}")
        return {
            "specialty": None,
            "clinic": None,
            "day_of_week": None,
            "doctor_name": None
        }

def make_accent_insensitive_pattern(text: str) -> str:
    pattern = ""
    for char in text:
        if char.lower() in ['a', 'e', 'i', 'o', 'u', 'á', 'é', 'í', 'ó', 'ú', 'ü']:
            pattern += "_"
        else:
            pattern += char
    return pattern

async def find_recommendations(db: AsyncSession, prefs: dict):
    """
    Finds up to 3 doctor assignments matching the extracted search preferences.
    """
    query = (
        select(DoctorMedicalCenter)
        .join(DoctorMedicalCenter.doctor)
        .join(DoctorMedicalCenter.center)
        .options(
            joinedload(DoctorMedicalCenter.doctor),
            joinedload(DoctorMedicalCenter.center)
        )
    )
    
    if prefs.get("doctor_name"):
        clean_name = prefs["doctor_name"]
        for prefix in ["dr. ", "dra. ", "dr ", "dra "]:
            if clean_name.lower().startswith(prefix):
                clean_name = clean_name[len(prefix):]
                break
        pattern = make_accent_insensitive_pattern(clean_name)
        query = query.where(Doctor.full_name.ilike(f"%{pattern}%"))
        
    if prefs.get("specialty"):
        pattern = make_accent_insensitive_pattern(prefs["specialty"])
        query = query.where(Doctor.specialty.ilike(f"%{pattern}%"))
        
    if prefs.get("clinic"):
        pattern = make_accent_insensitive_pattern(prefs["clinic"])
        query = query.where(MedicalCenter.name.ilike(f"%{pattern}%"))
        
    if prefs.get("day_of_week") is not None:
        query = query.join(DoctorMedicalCenter.schedules).where(
            Schedule.day_of_week == prefs["day_of_week"],
            Schedule.is_available == True
        )
        
    query = query.distinct().limit(3)
    result = await db.execute(query)
    return result.scalars().all()

async def get_gemini_response(history: list, current_message: str, db: AsyncSession) -> tuple:
    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.7
    )
    
    # 1. Extract search preferences
    prefs = await extract_search_preferences(current_message)
    has_prefs = any(v is not None for v in prefs.values())
    
    recommendations = []
    redirect_query = None
    not_found_doctor = False
    db_context = ""
    
    if has_prefs:
        assignments = await find_recommendations(db, prefs)
        
        # Check if they wanted a specific doctor by name, but we found nothing
        if prefs.get("doctor_name") and not assignments:
            not_found_doctor = True
            db_context = f"\n[INFO BASE DE DATOS]: El usuario buscó al médico '{prefs['doctor_name']}', pero NO se encuentra en el sistema. Debes responder aclarando amigablemente que no se encontró a ese doctor registrado."
        else:
            if assignments:
                db_context = f"\n[INFO BASE DE DATOS]: Se encontraron las siguientes recomendaciones de doctores:\n"
                for assign in assignments:
                    doc = assign.doctor
                    center = assign.center
                    db_context += f"- Dr. {doc.full_name}, Especialidad: {doc.specialty}, Clínica: {center.name}, Tarifa: Bs. {doc.consultation_fee or 'No especificado'}\n"
                    
                    recommendations.append({
                        "assignment_id": assign.id,
                        "doctor_name": doc.full_name,
                        "specialty": doc.specialty,
                        "clinic_name": center.name,
                        "consultation_fee": float(doc.consultation_fee) if doc.consultation_fee else None
                    })
                
                # Build redirect query
                redirect_query = {}
                if prefs.get("specialty"):
                    redirect_query["specialty"] = prefs["specialty"]
                
                search_terms = []
                if prefs.get("clinic"):
                    search_terms.append(prefs["clinic"])
                if search_terms:
                    redirect_query["search"] = " ".join(search_terms)
            else:
                db_context = "\n[INFO BASE DE DATOS]: No se encontraron doctores que coincidan con las preferencias (día, clínica o especialidad) del usuario en nuestro registro."
                
    try:
        specialties = await get_doctor_specialties(db)
        specialties_str = ", ".join(specialties) if specialties else "Ninguna registrada"
    except Exception:
        specialties_str = "Cardiología, Pediatría, Dermatología" # Fallback
        
    sys_prompt = f"""Eres un asistente médico virtual amigable en un portal de salud. Resuelves dudas de pacientes y doctores. Acostumbras ser conciso y recordar que no puedes dar diagnósticos definitivos y deben consultar a su médico.
    
    {db_context}
    
    IMPORTANTE PARA TRIAJE Y AGENDAMIENTO:
    Si el usuario describe síntomas, dolencias o expresa explícitamente su deseo de agendar una cita médica o ver a un especialista (sin indicar un médico concreto o preferencias específicas de clínicas/días), tu deber es identificar qué especialidad médica es la más adecuada para su caso.
    Especialidades médicas disponibles actualmente: {specialties_str}.
    Si logras identificar que el paciente necesita ver a un especialista de esta lista, debes recomendarle brevemente a ese especialista y OBLIGATORIAMENTE agregar el siguiente comando EXACTO al final de tu respuesta (reemplazando NombreDeLaEspecialidad por la elegida):
    [ACTION:MAP:NombreDeLaEspecialidad]
    
    Si hay resultados de base de datos arriba, utilízalos para responder amigablemente al usuario indicando que encontraste opciones de doctores que se ajustan a su búsqueda y que puede consultarlos y reservar abajo.
    Si se activó la indicación de que no se encontró el doctor (not_found_doctor), responde explícita y cordialmente aclarando que no se encontró a dicho doctor en el sistema.
    """
    
    messages = [
        SystemMessage(content=sys_prompt)
    ]
    
    # Populate history for context
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
            
    # Append the newest message
    messages.append(HumanMessage(content=current_message))
    
    # Call Gemini Model
    response = await llm.ainvoke(messages)
    return response.content, recommendations, redirect_query, not_found_doctor
