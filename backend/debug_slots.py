import asyncio
from app.core.database import AsyncSessionLocal
from app.models.appointment import Appointment
from sqlalchemy import select

async def run():
    async with AsyncSessionLocal() as db:
        appts = await db.execute(select(Appointment))
        for a in appts.scalars().all():
            print(f"ID: {a.id}, Date: {a.appointment_date}, TZ: {a.appointment_date.tzinfo}, Status: {a.status}")

if __name__ == "__main__":
    asyncio.run(run())
