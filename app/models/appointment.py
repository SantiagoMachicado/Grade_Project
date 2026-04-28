import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models import Base

class AppointmentStatusEnum(str, enum.Enum):
    PENDING = "pendiente"
    CONFIRMED = "confirmada"
    CANCELLED = "cancelada"
    COMPLETED = "completada"

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.user_id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.user_id"), nullable=True)
    center_id = Column(Integer, ForeignKey("medical_centers.id"), nullable=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default=AppointmentStatusEnum.PENDING.value)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    center = relationship("MedicalCenter", back_populates="appointments")
    schedule = relationship("Schedule")
