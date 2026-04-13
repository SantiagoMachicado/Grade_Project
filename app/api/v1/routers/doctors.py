from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.crud import crud_user
from app.schemas.user import DoctorResponse, UserUpdate
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[DoctorResponse])
async def read_doctors(
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    doctors = await crud_user.get_all_doctors(db, skip=skip, limit=limit)
    return doctors

@router.get("/{doctor_id}", response_model=DoctorResponse)
async def read_doctor(
    doctor_id: int, 
    db: AsyncSession = Depends(get_db)
):
    doctor = await crud_user.get_doctor(db, user_id=doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    return doctor

@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int, 
    doctor_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = await crud_user.update_doctor(db, user_id=doctor_id, updates=doctor_in)
    return doctor

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = await crud_user.get_doctor(db, user_id=doctor_id)
    if not doctor:
         raise HTTPException(status_code=404, detail="Doctor no encontrado")
    await crud_user.delete_user(db, user_id=doctor.user_id)
    return None
