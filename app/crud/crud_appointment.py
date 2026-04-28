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
    from sqlalchemy.orm import selectinload
    from app.models.user import Doctor, Patient
    result = await db.execute(
        select(Appointment)
        .where(Appointment.patient_id == patient_id)
        .options(
            selectinload(Appointment.doctor).selectinload(Doctor.user),
            selectinload(Appointment.center),
            selectinload(Appointment.patient).selectinload(Patient.user)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_appointments_by_doctor(db: AsyncSession, doctor_id: int, skip: int = 0, limit: int = 100):
    from sqlalchemy.orm import selectinload
    from app.models.user import Doctor, Patient
    result = await db.execute(
        select(Appointment)
        .where(Appointment.doctor_id == doctor_id)
        .options(
            selectinload(Appointment.patient).selectinload(Patient.user),
            selectinload(Appointment.doctor).selectinload(Doctor.user),
            selectinload(Appointment.center)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_doctor_agenda(db: AsyncSession, doctor_id: int, target_date: str):
    from app.models.user import Patient, Doctor
    from app.models.clinic import DoctorMedicalCenter
    from sqlalchemy.orm import selectinload
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from app.schemas.appointment import AgendaSlotResponse, AgendaSlotType
    
    t_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    dow = t_date.weekday()
    
    # 1. Fetch schedules
    schedules_result = await db.execute(
        select(Schedule)
        .join(DoctorMedicalCenter)
        .where(
            DoctorMedicalCenter.doctor_id == doctor_id,
            Schedule.day_of_week == dow,
            Schedule.is_available == True
        )
        .options(selectinload(Schedule.assignment).selectinload(DoctorMedicalCenter.center))
    )
    schedules = schedules_result.scalars().all()
    
    # 2. Fetch appointments
    appts_result = await db.execute(
        select(Appointment)
        .where(
            Appointment.doctor_id == doctor_id,
            func.date(Appointment.appointment_date) == t_date,
            Appointment.status != AppointmentStatusEnum.CANCELLED.value
        )
        .options(
            selectinload(Appointment.patient).selectinload(Patient.user),
            selectinload(Appointment.center),
            selectinload(Appointment.doctor).selectinload(Doctor.user)
        )
    )
    appointments = appts_result.scalars().all()
    
    appt_dict = {}
    for appt in appointments:
        dt = appt.appointment_date
        if dt.tzinfo is not None:
            dt = dt.astimezone()
        time_key = dt.time().replace(second=0, microsecond=0)
        appt_dict[time_key] = appt
    
    slots = []
    for schedule in schedules:
        current_time = schedule.start_time
        center = schedule.assignment.center
        
        while current_time < schedule.end_time:
            time_key = current_time.replace(second=0, microsecond=0)
            time_str = current_time.strftime("%H:%M")
            if time_key in appt_dict:
                appt = appt_dict[time_key]
                slots.append(AgendaSlotResponse(
                    time=time_str,
                    type=AgendaSlotType.APPOINTMENT,
                    center=center,
                    appointment=appt
                ))
            else:
                slots.append(AgendaSlotResponse(
                    time=time_str,
                    type=AgendaSlotType.AVAILABLE,
                    center=center,
                    appointment=None
                ))
            
            # add 30 min
            dt = datetime.combine(t_date, current_time) + timedelta(minutes=30)
            current_time = dt.time()
            
    slots.sort(key=lambda x: x.time)
    return slots

async def create_appointment(db: AsyncSession, appointment: AppointmentCreate, patient_id: int) -> Appointment:
    # 1. El doctor existe
    result_doc = await db.execute(select(Doctor).where(Doctor.user_id == appointment.doctor_id))
    doctor = result_doc.scalars().first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")

    appt_day_of_week = appointment.appointment_date.weekday()
    appt_time = appointment.appointment_date.time()

    from app.models.clinic import DoctorMedicalCenter
    # 2. El doctor tiene horario en ese lapso de tiempo en ese centro médico
    result_sched = await db.execute(
        select(Schedule)
        .join(DoctorMedicalCenter, Schedule.assignment_id == DoctorMedicalCenter.id)
        .where(
            and_(
                DoctorMedicalCenter.doctor_id == appointment.doctor_id,
                DoctorMedicalCenter.center_id == appointment.center_id,
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
        schedule_id=schedule.id,
        appointment_date=appointment.appointment_date,
        notes=appointment.notes
    )
    db.add(db_appt)
    await db.commit()
    
    from sqlalchemy.orm import selectinload
    from app.models.user import Patient
    stmt = select(Appointment).where(Appointment.id == db_appt.id).options(
        selectinload(Appointment.doctor).selectinload(Doctor.user),
        selectinload(Appointment.center),
        selectinload(Appointment.patient).selectinload(Patient.user)
    )
    res = await db.execute(stmt)
    return res.scalars().first()

async def update_appointment(db: AsyncSession, appointment_id: int, appointment: AppointmentCreate, patient_id: int) -> Appointment:
    appt = await get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    if appt.patient_id != patient_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta cita")
        
    if appt.status == AppointmentStatusEnum.CONFIRMED.value:
        raise HTTPException(status_code=400, detail="No se puede reprogramar una cita que ya está confirmada")

    # 1. El doctor existe
    result_doc = await db.execute(select(Doctor).where(Doctor.user_id == appointment.doctor_id))
    doctor = result_doc.scalars().first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")

    appt_day_of_week = appointment.appointment_date.weekday()
    appt_time = appointment.appointment_date.time()

    from app.models.clinic import DoctorMedicalCenter
    # 2. El doctor tiene horario en ese lapso de tiempo en ese centro médico
    result_sched = await db.execute(
        select(Schedule)
        .join(DoctorMedicalCenter, Schedule.assignment_id == DoctorMedicalCenter.id)
        .where(
            and_(
                DoctorMedicalCenter.doctor_id == appointment.doctor_id,
                DoctorMedicalCenter.center_id == appointment.center_id,
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

    # 3. No hay una cita que se sobreponga (ignorando esta misma cita)
    result_appt = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.appointment_date == appointment.appointment_date,
                Appointment.status != AppointmentStatusEnum.CANCELLED.value,
                Appointment.id != appointment_id
            )
        )
    )
    existing_appt = result_appt.scalars().first()
    if existing_appt:
        raise HTTPException(status_code=400, detail="Este horario ya se encuentra ocupado")

    appt.doctor_id = appointment.doctor_id
    appt.center_id = appointment.center_id
    appt.schedule_id = schedule.id
    appt.appointment_date = appointment.appointment_date
    appt.notes = appointment.notes
    appt.status = AppointmentStatusEnum.PENDING.value
    
    await db.commit()
    
    from sqlalchemy.orm import selectinload
    from app.models.user import Patient
    stmt = select(Appointment).where(Appointment.id == appointment_id).options(
        selectinload(Appointment.doctor).selectinload(Doctor.user),
        selectinload(Appointment.center),
        selectinload(Appointment.patient).selectinload(Patient.user)
    )
    res = await db.execute(stmt)
    return res.scalars().first()

async def update_appointment_status(db: AsyncSession, appointment_id: int, update: AppointmentUpdateStatus) -> Appointment:
    appt = await get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    appt.status = update.status.value
    await db.commit()
    
    from sqlalchemy.orm import selectinload
    from app.models.user import Doctor, Patient
    stmt = select(Appointment).where(Appointment.id == appointment_id).options(
        selectinload(Appointment.doctor).selectinload(Doctor.user),
        selectinload(Appointment.center),
        selectinload(Appointment.patient).selectinload(Patient.user)
    )
    res = await db.execute(stmt)
    return res.scalars().first()

async def delete_appointment(db: AsyncSession, appointment_id: int):
    appt = await get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    await db.delete(appt)
    await db.commit()
    return True
