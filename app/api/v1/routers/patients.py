from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.crud import crud_user
from app.schemas.user import PatientResponse, UserUpdate
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[PatientResponse])
async def read_patients(
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patients = await crud_user.get_all_patients(db, skip=skip, limit=limit)
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
async def read_patient(
    patient_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = await crud_user.get_patient(db, user_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int, 
    patient_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = await crud_user.update_patient(db, user_id=patient_id, updates=patient_in)
    return patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = await crud_user.get_patient(db, user_id=patient_id)
    if not patient:
         raise HTTPException(status_code=404, detail="Paciente no encontrado")
    await crud_user.delete_user(db, user_id=patient.user_id)
    return None
