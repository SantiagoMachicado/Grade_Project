import asyncio
from app.core.database import engine
from app.models import Base

# Modelos que deben registrarse
from app.models.user import User, Patient, Doctor
from app.models.clinic import MedicalCenter, Schedule
from app.models.appointment import Appointment

async def reset_db():
    print("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables based on new models...")
        await conn.run_sync(Base.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(reset_db())
