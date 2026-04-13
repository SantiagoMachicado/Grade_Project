from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin, get_current_doctor
from app.crud import crud_clinic
from app.schemas.clinic import (
    MedicalCenterCreate, MedicalCenterUpdate, MedicalCenterResponse,
    ScheduleCreate, ScheduleResponse
)
from app.models.user import User, Doctor

router = APIRouter()

@router.get("/", response_model=List[MedicalCenterResponse])
async def read_medical_centers(
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    centers = await crud_clinic.get_all_medical_centers(db, skip=skip, limit=limit)
    return centers

@router.post("/", response_model=MedicalCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_center(
    center_in: MedicalCenterCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    center = await crud_clinic.create_medical_center(db, center=center_in)
    return center

@router.get("/{center_id}", response_model=MedicalCenterResponse)
async def read_medical_center(
    center_id: int, 
    db: AsyncSession = Depends(get_db)
):
    center = await crud_clinic.get_medical_center(db, center_id=center_id)
    if not center:
        raise HTTPException(status_code=404, detail="Centro médico no encontrado")
    return center

@router.put("/{center_id}", response_model=MedicalCenterResponse)
async def update_medical_center(
    center_id: int, 
    center_in: MedicalCenterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    center = await crud_clinic.update_medical_center(db, center_id=center_id, updates=center_in)
    return center

@router.delete("/{center_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_center(
    center_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await crud_clinic.delete_medical_center(db, center_id=center_id)
    return None

# ------------- Schedules --------------

@router.get("/schedules/doctor/{doctor_id}", response_model=List[ScheduleResponse])
async def read_doctor_schedules(
    doctor_id: int, 
    db: AsyncSession = Depends(get_db)
):
    schedules = await crud_clinic.get_schedules_by_doctor(db, doctor_id=doctor_id)
    return schedules

@router.post("/schedules/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor_schedule(
    schedule_in: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    # Forzamos que el schedule sea de el mismo doctor que está logueado
    if schedule_in.doctor_id != current_doctor.user_id:
        raise HTTPException(status_code=403, detail="No puedes crear horarios para otro médico")
        
    schedule = await crud_clinic.create_schedule(db, schedule=schedule_in)
    return schedule

@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor_schedule(
    schedule_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await crud_clinic.delete_schedule(db, schedule_id=schedule_id)
    return None
