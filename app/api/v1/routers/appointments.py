from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_patient
from app.crud import crud_appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdateStatus, AppointmentResponse
from app.models.user import User, Patient

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment_endpoint(
    appointment_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    return await crud_appointment.create_appointment(db=db, appointment=appointment_in, patient_id=current_patient.user_id)

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
async def read_patient_appointments(
    patient_id: int,
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_appointment.get_appointments_by_patient(db, patient_id=patient_id, skip=skip, limit=limit)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse])
async def read_doctor_appointments(
    doctor_id: int,
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_appointment.get_appointments_by_doctor(db, doctor_id=doctor_id, skip=skip, limit=limit)

@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status_endpoint(
    appointment_id: int,
    status_in: AppointmentUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_appointment.update_appointment_status(db, appointment_id=appointment_id, update=status_in)

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment_endpoint(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await crud_appointment.delete_appointment(db, appointment_id=appointment_id)
    return None
