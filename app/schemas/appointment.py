from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.appointment import AppointmentStatusEnum
from app.schemas.user import PatientResponse, DoctorResponse
from app.schemas.clinic import MedicalCenterResponse

class AppointmentBase(BaseModel):
    appointment_date: datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    doctor_id: int
    center_id: int

class AppointmentUpdateStatus(BaseModel):
    status: AppointmentStatusEnum

class AppointmentUpdateReport(BaseModel):
    medical_report: str

class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    center_id: int
    status: AppointmentStatusEnum
    medical_report: Optional[str] = None
    notified_24h: bool = False
    notified_3h: bool = False
    
    patient: Optional[PatientResponse] = None
    doctor: Optional[DoctorResponse] = None
    center: Optional[MedicalCenterResponse] = None
    model_config = {"from_attributes": True}

import enum
class AgendaSlotType(str, enum.Enum):
    AVAILABLE = "available"
    APPOINTMENT = "appointment"

class AgendaSlotResponse(BaseModel):
    time: str
    type: AgendaSlotType
    center: Optional[MedicalCenterResponse] = None
    appointment: Optional[AppointmentResponse] = None
