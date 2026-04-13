from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.clinic import MedicalCenter, Schedule
from app.schemas.clinic import MedicalCenterCreate, MedicalCenterUpdate, ScheduleCreate, ScheduleUpdate

async def get_medical_center(db: AsyncSession, center_id: int) -> MedicalCenter | None:
    result = await db.execute(select(MedicalCenter).where(MedicalCenter.id == center_id))
    return result.scalars().first()

async def get_all_medical_centers(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(MedicalCenter).offset(skip).limit(limit))
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
    result = await db.execute(select(Schedule).where(Schedule.doctor_id == doctor_id))
    return result.scalars().all()

async def create_schedule(db: AsyncSession, schedule: ScheduleCreate) -> Schedule:
    db_schedule = Schedule(
        doctor_id=schedule.doctor_id,
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
