import asyncio
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.models.appointment import Appointment
from app.models.user import Doctor
from app.models.clinic import MedicalCenter, DoctorMedicalCenter, Schedule

async def main():
    async with AsyncSessionLocal() as db:
        print("--- DOCTORS ---")
        docs = await db.execute(select(Doctor))
        for d in docs.scalars().all():
            print(f"ID: {d.user_id}, Name: {d.full_name}, Specialty: {d.specialty}, Fee: {d.consultation_fee}")
            
        print("\n--- CLINICS ---")
        clinics = await db.execute(select(MedicalCenter))
        for c in clinics.scalars().all():
            print(f"ID: {c.id}, Name: {c.name}")
            
        print("\n--- ASSIGNMENTS ---")
        assigns = await db.execute(
            select(DoctorMedicalCenter)
            .options(
                selectinload(DoctorMedicalCenter.doctor),
                selectinload(DoctorMedicalCenter.center),
                selectinload(DoctorMedicalCenter.schedules)
            )
        )
        for a in assigns.scalars().all():
            print(f"AssignID: {a.id}, Doctor: {a.doctor.full_name}, Clinic: {a.center.name}")
            for s in a.schedules:
                print(f"  Schedule - Day: {s.day_of_week}, Start: {s.start_time}, End: {s.end_time}, Available: {s.is_available}")

if __name__ == "__main__":
    asyncio.run(main())
