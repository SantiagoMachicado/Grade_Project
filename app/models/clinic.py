from sqlalchemy import Column, Integer, String, Time, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.models import Base

class MedicalCenter(Base):
    __tablename__ = "medical_centers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    phone = Column(String(20), nullable=True)
    
    @property
    def location_wkt(self):
        from geoalchemy2.shape import to_shape
        if self.location is not None:
            return to_shape(self.location).wkt
        return None
    
    appointments = relationship("Appointment", back_populates="center", cascade="all, delete-orphan")

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.user_id", ondelete="CASCADE"), nullable=True)
    day_of_week = Column(Integer, nullable=True)  # 0 to 6
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    
    doctor = relationship("Doctor", back_populates="schedules")
