from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_user import get_doctor_specialties

async def get_gemini_response(history: list, current_message: str, db: AsyncSession) -> str:
    # Initialize the LLM. It automatically looks for GOOGLE_API_KEY
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7
    )
    
    try:
        specialties = await get_doctor_specialties(db)
        specialties_str = ", ".join(specialties) if specialties else "Ninguna registrada"
    except Exception:
        specialties_str = "Cardiología, Pediatría, Dermatología" # Fallback
        
    sys_prompt = f"""Eres un asistente médico virtual amigable en un portal de salud. Resuelves dudas de pacientes y doctores. Acostumbras ser conciso y recordar que no puedes dar diagnósticos definitivos y deben consultar a su médico.
    
    IMPORTANTE PARA TRIAJE Y AGENDAMIENTO:
    Si el usuario describe síntomas, dolencias o expresa explícitamente su deseo de agendar una cita médica o ver a un especialista, tu deber es identificar qué especialidad médica es la más adecuada para su caso.
    Especialidades médicas disponibles actualmente: {specialties_str}.
    
    Si logras identificar que el paciente necesita ver a un especialista de esta lista, debes recomendarle brevemente a ese especialista y OBLIGATORIAMENTE agregar el siguiente comando EXACTO al final de tu respuesta (reemplazando NombreDeLaEspecialidad por la elegida):
    [ACTION:MAP:NombreDeLaEspecialidad]
    
    Ejemplo de respuesta tuya: "Parece que esos síntomas podrían requerir evaluación de un cardiólogo. Te redirigiré a nuestro mapa de clínicas filtrado. [ACTION:MAP:Cardiología]"
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
    return response.content
