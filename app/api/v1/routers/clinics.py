from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_admin, get_current_doctor
from app.crud import crud_clinic
from app.schemas.clinic import (
    MedicalCenterCreate, MedicalCenterUpdate, MedicalCenterResponse,
    ScheduleCreate, ScheduleResponse, DoctorMedicalCenterResponse
)
from app.models.user import User, Doctor

router = APIRouter()

@router.get("/assignments", response_model=List[DoctorMedicalCenterResponse])
async def read_assignments(
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    assignments = await crud_clinic.get_doctor_assignments(db, skip=skip, limit=limit)
    return assignments

@router.get("/assignments/lookup", response_model=DoctorMedicalCenterResponse)
async def lookup_assignment(
    doctor_id: int,
    center_id: int,
    db: AsyncSession = Depends(get_db)
):
    assignment = await crud_clinic.get_assignment_by_doctor_center(db, doctor_id=doctor_id, center_id=center_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return await crud_clinic.get_doctor_assignment(db, assignment_id=assignment.id)

@router.get("/assignments/{assignment_id}", response_model=DoctorMedicalCenterResponse)
async def read_assignment(
    assignment_id: int, 
    db: AsyncSession = Depends(get_db)
):
    assignment = await crud_clinic.get_doctor_assignment(db, assignment_id=assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return assignment

@router.get("/assignments/{assignment_id}/slots")
async def read_assignment_slots(
    assignment_id: int, 
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    slots = await crud_clinic.get_available_slots_for_assignment(db, assignment_id=assignment_id, days=days)
    return slots

from typing import Optional

@router.get("/", response_model=List[MedicalCenterResponse])
async def read_medical_centers(
    specialty: Optional[str] = None,
    name: Optional[str] = None,
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    centers = await crud_clinic.get_all_medical_centers(db, skip=skip, limit=limit, specialty=specialty, name=name)
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
    # Primero buscamos a quién le pertenece el assignment
    from app.crud.crud_clinic import get_doctor_assignments
    from sqlalchemy.future import select
    from app.models.clinic import DoctorMedicalCenter
    result = await db.execute(select(DoctorMedicalCenter).where(DoctorMedicalCenter.id == schedule_in.assignment_id))
    assignment = result.scalars().first()
    
    if not assignment or assignment.doctor_id != current_doctor.user_id:
        raise HTTPException(status_code=403, detail="No puedes crear horarios para una clínica a la que no estás asignado")
        
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
