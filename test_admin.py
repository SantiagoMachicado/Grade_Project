import asyncio
import traceback
from app.core.database import AsyncSessionLocal
from app.schemas.user import UserCreate
from app.crud.crud_user import create_user

async def main():
    try:
        async with AsyncSessionLocal() as db:
            user = UserCreate(email="testadmin3@saludbolivia.com", password="Password123!", role="admin", full_name="Administrador")
            await create_user(db, user)
            print("SUCCESS")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
