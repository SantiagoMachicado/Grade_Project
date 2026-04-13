from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException
from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.clinic import Schedule
from app.models.user import Doctor
from app.schemas.appointment import AppointmentCreate, AppointmentUpdateStatus

async def get_appointment(db: AsyncSession, appointment_id: int) -> Appointment | None:
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalars().first()

async def get_appointments_by_patient(db: AsyncSession, patient_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Appointment).where(Appointment.patient_id == patient_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_appointments_by_doctor(db: AsyncSession, doctor_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Appointment).where(Appointment.doctor_id == doctor_id).offset(skip).limit(limit))
    return result.scalars().all()

async def create_appointment(db: AsyncSession, appointment: AppointmentCreate, patient_id: int) -> Appointment:
    # 1. El doctor existe
    result_doc = await db.execute(select(Doctor).where(Doctor.user_id == appointment.doctor_id))
    doctor = result_doc.scalars().first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")

    appt_day_of_week = appointment.appointment_date.weekday()
    appt_time = appointment.appointment_date.time()

    # 2. El doctor tiene horario en ese lapso de tiempo
    result_sched = await db.execute(
        select(Schedule).where(
            and_(
                Schedule.doctor_id == appointment.doctor_id,
                Schedule.day_of_week == appt_day_of_week,
                Schedule.start_time <= appt_time,
                Schedule.end_time >= appt_time,
                Schedule.is_available == True
            )
        )
    )
    schedule = result_sched.scalars().first()
    if not schedule:
        raise HTTPException(status_code=400, detail="El doctor no tiene disponibilidad en este horario")

    # 3. No hay una cita que se sobreponga
    result_appt = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.appointment_date == appointment.appointment_date,
                Appointment.status != AppointmentStatusEnum.CANCELLED.value
            )
        )
    )
    existing_appt = result_appt.scalars().first()
    if existing_appt:
        raise HTTPException(status_code=400, detail="Este horario ya se encuentra ocupado")

    db_appt = Appointment(
        patient_id=patient_id,
        doctor_id=appointment.doctor_id,
        center_id=appointment.center_id,
        appointment_date=appointment.appointment_date,
        notes=appointment.notes
    )
    db.add(db_appt)
    await db.commit()
    await db.refresh(db_appt)
    return db_appt

async def update_appointment_status(db: AsyncSession, appointment_id: int, update: AppointmentUpdateStatus) -> Appointment:
    appt = await get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    appt.status = update.status.value
    await db.commit()
    await db.refresh(appt)
    return appt

async def delete_appointment(db: AsyncSession, appointment_id: int):
    appt = await get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    await db.delete(appt)
    await db.commit()
    return True
