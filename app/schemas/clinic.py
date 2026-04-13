from pydantic import BaseModel
from datetime import time
from typing import Optional

class MedicalCenterBase(BaseModel):
    name: str
    address: Optional[str] = None
    location_wkt: Optional[str] = None  # WKT representation (e.g. POINT(longitude latitude))
    phone: Optional[str] = None

class MedicalCenterCreate(MedicalCenterBase):
    pass

class MedicalCenterUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    location_wkt: Optional[str] = None
    phone: Optional[str] = None

class MedicalCenterResponse(MedicalCenterBase):
    id: int
    model_config = {"from_attributes": True}

class ScheduleBase(BaseModel):
    day_of_week: int  # 0 to 6
    start_time: time
    end_time: time
    is_available: bool = True

class ScheduleCreate(ScheduleBase):
    doctor_id: int

class ScheduleUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None

class ScheduleResponse(ScheduleBase):
    id: int
    doctor_id: int
    model_config = {"from_attributes": True}
