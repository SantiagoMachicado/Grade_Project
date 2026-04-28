from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.user import User, Patient, Doctor, RoleEnum
from app.schemas.user import UserCreate, UserUpdate
from app.core import security

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = security.get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password, role=user.role.value)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    if user.role == RoleEnum.PATIENT:
        db_patient = Patient(
            user_id=db_user.id,
            full_name=user.full_name,
            birth_date=user.birth_date,
            phone=user.phone,
            medical_history=user.medical_history
        )
        db.add(db_patient)

    elif user.role == RoleEnum.DOCTOR:
        if not user.specialty or not user.license_number:
            raise HTTPException(status_code=400, detail="Especialidad y número de licencia obligatorios para doctores")
        db_doctor = Doctor(
            user_id=db_user.id,
            full_name=user.full_name,
            specialty=user.specialty,
            license_number=user.license_number,
            bio=user.bio,
            consultation_fee=user.consultation_fee
        )
        db.add(db_doctor)
    
    await db.commit()
    return db_user

async def get_patient(db: AsyncSession, user_id: int) -> Patient | None:
    result = await db.execute(select(Patient).where(Patient.user_id == user_id))
    return result.scalars().first()

async def get_all_patients(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Patient).offset(skip).limit(limit))
    return result.scalars().all()

async def get_doctor(db: AsyncSession, user_id: int) -> Doctor | None:
    result = await db.execute(select(Doctor).where(Doctor.user_id == user_id))
    return result.scalars().first()

async def get_all_doctors(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Doctor).offset(skip).limit(limit))
    return result.scalars().all()

async def update_patient(db: AsyncSession, user_id: int, updates: UserUpdate) -> Patient:
    patient = await get_patient(db, user_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
    for key, value in updates.model_dump(exclude_unset=True).items():
        if hasattr(patient, key):
            setattr(patient, key, value)
            
    await db.commit()
    await db.refresh(patient)
    return patient

async def update_doctor(db: AsyncSession, user_id: int, updates: UserUpdate) -> Doctor:
    doctor = await get_doctor(db, user_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
        
    for key, value in updates.model_dump(exclude_unset=True).items():
        if hasattr(doctor, key):
            setattr(doctor, key, value)
            
    await db.commit()
    await db.refresh(doctor)
    return doctor

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.delete(user)
    await db.commit()
    return True

async def get_doctor_specialties(db: AsyncSession):
    result = await db.execute(select(Doctor.specialty).where(Doctor.specialty != None).distinct())
    return result.scalars().all()
