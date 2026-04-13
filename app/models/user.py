import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "medico"
    PATIENT = "paciente"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False) # Or Enum(RoleEnum) if preferred, using String(20) to match exact SQL definition
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    patient = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")
    doctor = relationship("Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Patient(Base):
    __tablename__ = "patients"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=True)
    phone = Column(String(20), nullable=True)
    medical_history = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

class Doctor(Base):
    __tablename__ = "doctors"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name = Column(String(255), nullable=False)
    specialty = Column(String(100), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    consultation_fee = Column(Numeric(10, 2), nullable=True)
    
    user = relationship("User", back_populates="doctor")
    schedules = relationship("Schedule", back_populates="doctor", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
