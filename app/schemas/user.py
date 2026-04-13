from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from decimal import Decimal
from app.models.user import RoleEnum

class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    full_name: str
    
    # Optional fields based on role
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None
    consultation_fee: Optional[Decimal] = None
    
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    medical_history: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None
    consultation_fee: Optional[Decimal] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    medical_history: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserResponse(UserBase):
    id: int
    model_config = {"from_attributes": True}

class PatientResponse(BaseModel):
    user_id: int
    full_name: str
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    medical_history: Optional[str] = None
    user: UserResponse
    model_config = {"from_attributes": True}

class DoctorResponse(BaseModel):
    user_id: int
    full_name: str
    specialty: str
    license_number: str
    bio: Optional[str] = None
    consultation_fee: Optional[Decimal] = None
    user: UserResponse
    model_config = {"from_attributes": True}
