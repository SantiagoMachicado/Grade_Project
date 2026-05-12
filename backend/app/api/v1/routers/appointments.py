from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_patient
from app.crud import crud_appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdateStatus, AppointmentResponse, AgendaSlotResponse
from app.models.user import User, Patient

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment_endpoint(
    appointment_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    return await crud_appointment.create_appointment(db=db, appointment=appointment_in, patient_id=current_patient.user_id)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_endpoint(
    appointment_id: int,
    appointment_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    return await crud_appointment.update_appointment(db=db, appointment_id=appointment_id, appointment=appointment_in, patient_id=current_patient.user_id)

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
async def read_patient_appointments(
    patient_id: int,
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    if current_patient.user_id != patient_id:
        raise HTTPException(status_code=403, detail="No puedes ver las citas de otro paciente")
    return await crud_appointment.get_appointments_by_patient(db, patient_id=patient_id, skip=skip, limit=limit)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse])
async def read_doctor_appointments(
    doctor_id: int,
    status: str = None,
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_appointment.get_appointments_by_doctor(db, doctor_id=doctor_id, skip=skip, limit=limit, status=status)

@router.get("/doctor/{doctor_id}/agenda", response_model=List[AgendaSlotResponse])
async def read_doctor_agenda(
    doctor_id: int,
    date: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_appointment.get_doctor_agenda(db, doctor_id=doctor_id, target_date=date)

from app.api.deps import get_current_doctor

@router.get("/doctor/{doctor_id}/stats")
async def read_doctor_stats(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    current_doctor = Depends(get_current_doctor)
):
    return await crud_appointment.get_doctor_stats(db, doctor_id=doctor_id)

@router.get("/doctor/{doctor_id}/dashboard")
async def read_doctor_dashboard(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    current_doctor = Depends(get_current_doctor)
):
    return await crud_appointment.get_doctor_dashboard_stats(db, doctor_id=doctor_id)

@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status_endpoint(
    appointment_id: int,
    status_in: AppointmentUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_appointment.update_appointment_status(db, appointment_id=appointment_id, update=status_in)

from app.schemas.appointment import AppointmentUpdateReport

@router.patch("/{appointment_id}/report", response_model=AppointmentResponse)
async def update_appointment_report_endpoint(
    appointment_id: int,
    report_in: AppointmentUpdateReport,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_appointment.update_appointment_report(db, appointment_id=appointment_id, report=report_in.medical_report)

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment_endpoint(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await crud_appointment.delete_appointment(db, appointment_id=appointment_id)
    return None
