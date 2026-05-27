import asyncio
from app.core.database import AsyncSessionLocal
from app.services.chat_service import get_gemini_response
from app.models.appointment import Appointment
from app.schemas.chat import Message

async def test():
    async with AsyncSessionLocal() as db:
        print("--- TEST 1: Búsqueda de médico específico existente ---")
        reply, recs, query, not_found = await get_gemini_response([], "Quiero ver al Dr. Alejandro Perez", db)
        print(f"Reply: {reply}")
        print(f"Recs: {recs}")
        print(f"Query: {query}")
        print(f"Not Found: {not_found}")
        
        print("\n--- TEST 2: Búsqueda de médico específico inexistente ---")
        reply, recs, query, not_found = await get_gemini_response([], "Quiero ver al Dr. Juan Nadie", db)
        print(f"Reply: {reply}")
        print(f"Recs: {recs}")
        print(f"Query: {query}")
        print(f"Not Found: {not_found}")
        
        print("\n--- TEST 3: Búsqueda por preferencia ---")
        reply, recs, query, not_found = await get_gemini_response([], "Quiero ver un cardiólogo los miércoles en Clínica del Sur", db)
        print(f"Reply: {reply}")
        print(f"Recs: {recs}")
        print(f"Query: {query}")
        print(f"Not Found: {not_found}")

if __name__ == "__main__":
    asyncio.run(test())
