import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock

from app.schemas.user import UserCreate, RoleEnum
from app.crud.crud_user import create_user

@pytest.mark.asyncio
async def test_i2_post_chat(client: AsyncClient, db_session):
    # Crear un paciente para loguearse
    await create_user(db_session, UserCreate(email="chat_user@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="Chat User"))
    
    # Login para obtener el token
    res_login = await client.post("/api/v1/auth/login", data={"username": "chat_user@x.com", "password": "securepass123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # I2: Interacción completa con endpoint /chat mockeando el LLM para evitar consumo de API y garantizar determinismo
    with patch("app.services.chat_service.ChatGoogleGenerativeAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        # Configuramos la respuesta simulada
        mock_ainvoke.return_value = MagicMock(content="Hola, ¿en qué te puedo ayudar?")
        
        request_data = {
            "history": [],
            "message": "Hola"
        }
        
        res = await client.post("/api/v1/chat/", json=request_data, headers=headers)
        
        assert res.status_code == 200
        data = res.json()
        assert "response" in data
        assert data["response"] == "Hola, ¿en qué te puedo ayudar?"
