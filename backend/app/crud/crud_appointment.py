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

async def get_doctor_stats(db: AsyncSession, doctor_id: int):
    from sqlalchemy import func
    from datetime import datetime
    from app.models.user import Doctor
    
    # Verify doctor
    doc_result = await db.execute(select(Doctor).where(Doctor.user_id == doctor_id))
    doctor = doc_result.scalars().first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    fee = float(doctor.consultation_fee) if doctor.consultation_fee else 0.0

    # Get all appointments for the doctor
    result = await db.execute(select(Appointment).where(Appointment.doctor_id == doctor_id))
    appointments = result.scalars().all()

    # Success Breakdown
    status_counts = {"completada": 0, "cancelada": 0, "ausente": 0, "pendiente": 0, "confirmada": 0}
    for appt in appointments:
        if appt.status in status_counts:
            status_counts[appt.status] += 1
            
    # For breakdown, we focus on completed, cancelled, ausente
    total_finished = status_counts["completada"] + status_counts["cancelada"] + status_counts["ausente"]
    breakdown = {
        "completed_pct": round((status_counts["completada"] / total_finished * 100) if total_finished > 0 else 0),
        "cancelled_pct": round((status_counts["cancelada"] / total_finished * 100) if total_finished > 0 else 0),
        "absent_pct": round((status_counts["ausente"] / total_finished * 100) if total_finished > 0 else 0)
    }

    # Time series (last 6 months)
    now = datetime.now()
    months_data = []
    # Spanish month names
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    
    total_active_patients = set()
    total_revenue = 0.0
    
    # We will build an array of 6 elements for the last 6 months including current
    for i in range(5, -1, -1):
        target_month = now.month - i
        target_year = now.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
            
        month_label = meses[target_month - 1]
        
        # Filter appointments in this month/year
        monthly_appts = [a for a in appointments if a.appointment_date.month == target_month and a.appointment_date.year == target_year]
        
        monthly_patients = set(a.patient_id for a in monthly_appts if a.status in ["completada", "confirmada"])
        monthly_revenue = sum(fee for a in monthly_appts if a.status == "completada")
        
        months_data.append({
            "month": month_label,
            "patients": len(monthly_patients),
            "revenue": monthly_revenue
        })
        
        total_active_patients.update(monthly_patients)
        total_revenue += monthly_revenue
        
    # Calculate avg revenue
    avg_revenue = round(total_revenue / 6, 2)
    
    return {
        "total_active_patients": len(total_active_patients),
        "total_revenue": total_revenue,
        "avg_revenue": avg_revenue,
        "revenue_growth": 12, # Static mock for now
        "breakdown": breakdown,
        "chart_data": months_data
    }

async def get_doctor_dashboard_stats(db: AsyncSession, doctor_id: int):
    from sqlalchemy import func
    from datetime import datetime, timedelta, timezone
    from app.models.user import Doctor
    
    # Verify doctor
    doc_result = await db.execute(select(Doctor).where(Doctor.user_id == doctor_id))
    doctor = doc_result.scalars().first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    # Get all appointments for the doctor
    result = await db.execute(select(Appointment).where(Appointment.doctor_id == doctor_id))
    appointments = result.scalars().all()
    
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    seven_days_ago = now - timedelta(days=7)
    
    # 1. Citas de hoy (Cualquier estado menos cancelada)
    today_appointments = [a for a in appointments if today_start <= a.appointment_date <= today_end and a.status != "cancelada"]
    
    # 2. Pacientes nuevos (últimos 7 días)
    # Group appointments by patient to find their first ever appointment
    all_appointments_sorted = sorted(appointments, key=lambda x: x.appointment_date)
    first_appointment_per_patient = {}
    for appt in all_appointments_sorted:
        if appt.patient_id not in first_appointment_per_patient:
            first_appointment_per_patient[appt.patient_id] = appt.appointment_date
            
    new_patients_count = sum(1 for date in first_appointment_per_patient.values() if seven_days_ago <= date <= now)
    
    # 3. Próxima cita (confirmada, desde ahora en adelante)
    future_confirmed = [a for a in appointments if a.appointment_date >= now and a.status == "confirmada"]
    future_confirmed.sort(key=lambda x: x.appointment_date)
    
    next_appointment = future_confirmed[0] if future_confirmed else None
    
    # 4. Siguientes citas (confirmadas, desde ahora, excluyendo la próxima)
    upcoming_appointments = future_confirmed[1:4] if len(future_confirmed) > 1 else []
    
    # 5. Citas no confirmadas (pendientes, desde hoy en adelante)
    unconfirmed = [a for a in appointments if a.appointment_date >= today_start and a.status == "pendiente"]
    unconfirmed.sort(key=lambda x: x.appointment_date)
    unconfirmed_appointments = unconfirmed[:3]
    
    # We need to manually load patient info to avoid selectinload issues if we don't have it loaded.
    # Actually, we can just return dicts.
    
    from app.models.user import Patient
    
    def format_appt(appt):
        if not appt: return None
        return {
            "id": appt.id,
            "patient_id": appt.patient_id,
            "appointment_date": appt.appointment_date.isoformat(),
            "status": appt.status,
            "notes": appt.notes
        }
        
    dashboard_data = {
        "today_appointments_count": len(today_appointments),
        "new_patients_count": new_patients_count,
        "next_appointment": format_appt(next_appointment),
        "upcoming_appointments": [format_appt(a) for a in upcoming_appointments],
        "unconfirmed_appointments": [format_appt(a) for a in unconfirmed_appointments]
    }
    
    # Populate patient names
    patient_ids = set()
    if next_appointment: patient_ids.add(next_appointment.patient_id)
    for a in upcoming_appointments: patient_ids.add(a.patient_id)
    for a in unconfirmed_appointments: patient_ids.add(a.patient_id)
    
    if patient_ids:
        patients_res = await db.execute(select(Patient).where(Patient.user_id.in_(patient_ids)))
        patients_map = {p.user_id: {"full_name": p.full_name} for p in patients_res.scalars().all()}
        
        if dashboard_data["next_appointment"]:
            dashboard_data["next_appointment"]["patient"] = patients_map.get(dashboard_data["next_appointment"]["patient_id"])
        
        for a in dashboard_data["upcoming_appointments"]:
            a["patient"] = patients_map.get(a["patient_id"])
            
        for a in dashboard_data["unconfirmed_appointments"]:
            a["patient"] = patients_map.get(a["patient_id"])
            
    return dashboard_data

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

async def get_appointments_by_doctor(db: AsyncSession, doctor_id: int, skip: int = 0, limit: int = 100, status: str = None):
    from sqlalchemy.orm import selectinload
    from app.models.user import Doctor, Patient
    
    query = select(Appointment).where(Appointment.doctor_id == doctor_id)
    
    if status:
        status_list = [s.strip().lower() for s in status.split(",")]
        print(f"DEBUG STATUS LIST: {status_list}")
        query = query.where(Appointment.status.in_(status_list))
        
    query = query.order_by(Appointment.appointment_date.desc()).options(
        selectinload(Appointment.patient).selectinload(Patient.user),
        selectinload(Appointment.doctor).selectinload(Doctor.user),
        selectinload(Appointment.center)
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
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

async def update_appointment_report(db: AsyncSession, appointment_id: int, report: str) -> Appointment:
    appt = await get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    appt.medical_report = report
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
