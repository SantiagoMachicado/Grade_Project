import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.appointment import Appointment
from app.models.user import Patient, Doctor
from app.services.email_service import send_notification_email
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def check_appointments_and_notify():
    print(f"[{datetime.now()}] Ejecutando tarea de notificación de citas...")
    
    async with AsyncSessionLocal() as session:
        # Usamos UTC para comparar con la base de datos (PostgreSQL timestamps con timezone)
        now = datetime.now(timezone.utc)
        time_24h = now + timedelta(hours=24)
        time_3h = now + timedelta(hours=3)
        
        # 1. Notificaciones de 24 Horas
        stmt_24 = select(Appointment).where(
            Appointment.status == "confirmada",
            Appointment.notified_24h == False,
            Appointment.appointment_date <= time_24h,
            Appointment.appointment_date > time_3h
        ).options(
            selectinload(Appointment.patient).selectinload(Patient.user),
            selectinload(Appointment.doctor)
        )
        
        result_24 = await session.execute(stmt_24)
        appointments_24 = result_24.scalars().all()
        
        for appt in appointments_24:
            if appt.patient and appt.patient.user and appt.patient.user.email:
                patient_name = appt.patient.full_name or "Paciente"
                doctor_name = appt.doctor.full_name if appt.doctor else "Médico asignado"
                appt_time = appt.appointment_date.astimezone().strftime("%d/%m/%Y a las %H:%M")
                
                body = f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #0284c7;">Recordatorio de Cita - Hospital Connect</h2>
                    <p>Hola <strong>{patient_name}</strong>,</p>
                    <p>Te recordamos que tienes una cita médica programada para mañana con el Dr./Dra. {doctor_name}.</p>
                    <p><strong>Fecha y Hora:</strong> {appt_time}</p>
                    <p>Por favor, intenta llegar 10 minutos antes de la hora acordada.</p>
                    <p><small>Este es un mensaje automático, por favor no respondas a este correo.</small></p>
                </div>
                """
                send_notification_email(appt.patient.user.email, "Recordatorio: Tienes una cita mañana", body)
            
            # Marcamos como notificado
            appt.notified_24h = True
            
        if appointments_24:
            await session.commit()
            print(f"[{datetime.now()}] {len(appointments_24)} notificaciones de 24h procesadas.")
            
        # 2. Notificaciones de 3 Horas
        stmt_3 = select(Appointment).where(
            Appointment.status == "confirmada",
            Appointment.notified_3h == False,
            Appointment.appointment_date <= time_3h,
            Appointment.appointment_date > now
        ).options(
            selectinload(Appointment.patient).selectinload(Patient.user),
            selectinload(Appointment.doctor)
        )
        
        result_3 = await session.execute(stmt_3)
        appointments_3 = result_3.scalars().all()
        
        for appt in appointments_3:
            if appt.patient and appt.patient.user and appt.patient.user.email:
                patient_name = appt.patient.full_name or "Paciente"
                doctor_name = appt.doctor.full_name if appt.doctor else "Médico asignado"
                appt_time = appt.appointment_date.astimezone().strftime("%H:%M")
                
                body = f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #ef4444;">¡Tu cita está a punto de comenzar!</h2>
                    <p>Hola <strong>{patient_name}</strong>,</p>
                    <p>Este es un último recordatorio de que tu consulta con el Dr./Dra. {doctor_name} será hoy a las <strong>{appt_time}</strong>.</p>
                    <p>Te esperamos.</p>
                </div>
                """
                send_notification_email(appt.patient.user.email, "Tu cita médica es en menos de 3 horas", body)
            
            # Marcamos ambas como notificadas por si la cita se programó tarde (ej. a 2 horas del inicio)
            appt.notified_3h = True
            appt.notified_24h = True 
            
        if appointments_3:
            await session.commit()
            print(f"[{datetime.now()}] {len(appointments_3)} notificaciones de 3h procesadas.")


def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Ejecutar la revisión cada 15 minutos (ajustable)
    # scheduler.add_job(check_appointments_and_notify, 'interval', minutes=15)
    scheduler.start()
    print("✅ Motor de tareas en segundo plano (APScheduler) iniciado.")
