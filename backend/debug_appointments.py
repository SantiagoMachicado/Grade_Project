import asyncio
from app.core.database import SessionLocal
from app.crud.crud_appointment import get_appointments_by_doctor

async def main():
    async with SessionLocal() as db:
        # Find a doctor
        from sqlalchemy import select
        from app.models.user import Doctor
        res = await db.execute(select(Doctor))
        doctor = res.scalars().first()
        if not doctor:
            print("No doctor found")
            return
            
        print(f"Doctor ID: {doctor.user_id}")
        appts = await get_appointments_by_doctor(db, doctor.user_id, status="confirmada,completada")
        for appt in appts:
            print(f"Appt {appt.id}: status={appt.status}")

if __name__ == "__main__":
    asyncio.run(main())
