from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException
from app.models.clinic import MedicalCenter, Schedule, DoctorMedicalCenter
from app.schemas.clinic import MedicalCenterCreate, MedicalCenterUpdate, ScheduleCreate, ScheduleUpdate

async def get_doctor_assignments(db: AsyncSession, skip: int = 0, limit: int = 100):
    from sqlalchemy.orm import selectinload
    from app.models.user import Doctor
    result = await db.execute(
        select(DoctorMedicalCenter)
        .options(
            selectinload(DoctorMedicalCenter.doctor).selectinload(Doctor.user), 
            selectinload(DoctorMedicalCenter.center)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_doctor_assignment(db: AsyncSession, assignment_id: int):
    from sqlalchemy.orm import selectinload
    from app.models.user import Doctor
    result = await db.execute(
        select(DoctorMedicalCenter)
        .where(DoctorMedicalCenter.id == assignment_id)
        .options(
            selectinload(DoctorMedicalCenter.doctor).selectinload(Doctor.user), 
            selectinload(DoctorMedicalCenter.center)
        )
    )
    return result.scalars().first()

async def get_assignment_by_doctor_center(db: AsyncSession, doctor_id: int, center_id: int):
    result = await db.execute(
        select(DoctorMedicalCenter)
        .where(
            DoctorMedicalCenter.doctor_id == doctor_id,
            DoctorMedicalCenter.center_id == center_id
        )
    )
    return result.scalars().first()

from datetime import date, datetime, timedelta
from typing import List, Dict

async def get_available_slots_for_assignment(db: AsyncSession, assignment_id: int, days: int = 30) -> List[Dict]:
    assignment = await get_doctor_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
    schedules = await db.execute(select(Schedule).where(Schedule.assignment_id == assignment_id, Schedule.is_available == True))
    schedules = schedules.scalars().all()
    if not schedules:
        return []

    sched_map = {}
    for s in schedules:
        if s.day_of_week not in sched_map:
            sched_map[s.day_of_week] = []
        sched_map[s.day_of_week].append(s)

    from app.models.appointment import Appointment, AppointmentStatusEnum
    from sqlalchemy import and_
    
    start_date = datetime.now()
    start_date_midnight = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=days)
    
    appts = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == assignment.doctor_id,
                Appointment.center_id == assignment.center_id,
                Appointment.appointment_date >= start_date_midnight,
                Appointment.appointment_date <= end_date,
                Appointment.status != AppointmentStatusEnum.CANCELLED.value
            )
        )
    )
    booked_times_str = []
    for appt in appts.scalars().all():
        dt = appt.appointment_date
        if dt.tzinfo is not None:
            # Strip timezone without shifting the hour (avoid local timezone mismatch)
            dt = dt.replace(tzinfo=None)
        booked_times_str.append(dt.strftime("%Y-%m-%d %H:%M"))
    
    available_days = []
    current_date = start_date.date()
    
    for i in range(days):
        target_date = current_date + timedelta(days=i)
        dow = target_date.weekday()
        
        if dow in sched_map:
            slots_for_day = []
            for s in sched_map[dow]:
                start_dt = datetime.combine(target_date, s.start_time)
                end_dt = datetime.combine(target_date, s.end_time)
                
                curr_dt = start_dt
                while curr_dt + timedelta(minutes=30) <= end_dt:
                    if curr_dt.date() >= start_date.date(): 
                        time_str = curr_dt.strftime("%H:%M")
                        curr_str = curr_dt.strftime("%Y-%m-%d %H:%M")
                        is_available = True
                        
                        # Bloquear si la cita es en menos de 3 horas o si ya está reservada
                        if curr_dt < start_date + timedelta(hours=3) or curr_str in booked_times_str:
                            is_available = False
                            
                        # Evitar duplicados si hay cruces de horarios en db
                        if not any(s['time'] == time_str for s in slots_for_day):
                            slots_for_day.append({
                                "time": time_str,
                                "available": is_available
                            })
                    curr_dt += timedelta(minutes=30)
            
            if slots_for_day:
                # Sort slots by time
                slots_for_day.sort(key=lambda x: x["time"])
                available_days.append({
                    "date": target_date.isoformat(),
                    "slots": slots_for_day
                })
                
    return available_days

async def get_medical_center(db: AsyncSession, center_id: int) -> MedicalCenter | None:
    result = await db.execute(select(MedicalCenter).where(MedicalCenter.id == center_id))
    return result.scalars().first()

async def get_all_medical_centers(db: AsyncSession, skip: int = 0, limit: int = 100, specialty: str = None, name: str = None):
    query = select(MedicalCenter)
    if specialty:
        from app.models.user import Doctor
        query = query.join(DoctorMedicalCenter, DoctorMedicalCenter.center_id == MedicalCenter.id).join(Doctor, Doctor.user_id == DoctorMedicalCenter.doctor_id).where(Doctor.specialty == specialty).distinct()
    
    if name:
        query = query.where(MedicalCenter.name.ilike(f"%{name}%"))
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_medical_center(db: AsyncSession, center: MedicalCenterCreate) -> MedicalCenter:
    location = f"SRID=4326;{center.location_wkt}" if center.location_wkt else None
    db_center = MedicalCenter(
        name=center.name,
        address=center.address,
        location=location,
        phone=center.phone
    )
    db.add(db_center)
    await db.commit()
    await db.refresh(db_center)
    return db_center

async def update_medical_center(db: AsyncSession, center_id: int, updates: MedicalCenterUpdate) -> MedicalCenter:
    center = await get_medical_center(db, center_id)
    if not center:
        raise HTTPException(status_code=404, detail="Centro médico no encontrado")
        
    if updates.name:
        center.name = updates.name
    if updates.address is not None:
        center.address = updates.address
    if updates.location_wkt:
        center.location = f"SRID=4326;{updates.location_wkt}"
    if updates.phone is not None:
        center.phone = updates.phone
            
    await db.commit()
    await db.refresh(center)
    return center

async def delete_medical_center(db: AsyncSession, center_id: int):
    center = await get_medical_center(db, center_id)
    if not center:
        raise HTTPException(status_code=404, detail="Centro médico no encontrado")
    await db.delete(center)
    await db.commit()
    return True

# Schedule CRUD
async def get_schedule(db: AsyncSession, schedule_id: int) -> Schedule | None:
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    return result.scalars().first()

async def get_schedules_by_doctor(db: AsyncSession, doctor_id: int):
    result = await db.execute(
        select(Schedule)
        .join(DoctorMedicalCenter, Schedule.assignment_id == DoctorMedicalCenter.id)
        .where(DoctorMedicalCenter.doctor_id == doctor_id)
    )
    return result.scalars().all()

async def create_schedule(db: AsyncSession, schedule: ScheduleCreate) -> Schedule:
    db_schedule = Schedule(
        assignment_id=schedule.assignment_id,
        day_of_week=schedule.day_of_week,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        is_available=schedule.is_available
    )
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule

async def delete_schedule(db: AsyncSession, schedule_id: int):
    schedule = await get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    await db.delete(schedule)
    await db.commit()
    return True
