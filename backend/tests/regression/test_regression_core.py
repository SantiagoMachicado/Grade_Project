import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone

from app.schemas.user import UserCreate, RoleEnum
from app.crud.crud_user import create_user

import pytest_asyncio

@pytest_asyncio.fixture
async def regression_users(db_session):
    p = await create_user(db_session, UserCreate(email="reg_pat@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="Pat Reg"))
    return p

@pytest.mark.asyncio
async def test_r1_login_core_stability(client: AsyncClient, regression_users):
    # R1: Asegurar que el Login principal nunca se rompa y retorne el token correcto
    res = await client.post("/api/v1/auth/login", data={"username": "reg_pat@x.com", "password": "securepass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

@pytest.mark.asyncio
async def test_r2_r4_appointment_creation_stability(client: AsyncClient, regression_users):
    # R4: Asegurar que las validaciones de fechas pasadas en los modelos sigan aplicándose a nivel de API
    res_login = await client.post("/api/v1/auth/login", data={"username": "reg_pat@x.com", "password": "securepass123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    past_date = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
    appt_data = {
        "doctor_id": 999,
        "center_id": 999,
        "appointment_date": past_date,
        "notes": "Regression"
    }
    
    res = await client.post("/api/v1/appointments/", json=appt_data, headers=headers)
    # Debe ser rechazado por Pydantic (422 Unprocessable Entity)
    assert res.status_code == 422
    assert "future" in res.text.lower() or "date" in res.text.lower()

@pytest.mark.asyncio
async def test_r5_patient_profile_relationships(client: AsyncClient, regression_users, db_session):
    # R5: Asegurar que al buscar a un paciente, sus relaciones anidadas (User -> email) sigan existiendo
    patient = regression_users
    
    # Intentar obtener el perfil del paciente
    # NOTA: En la API actual de /patients no hay un get_me explícito, usamos auth
    res_login = await client.post("/api/v1/auth/login", data={"username": "reg_pat@x.com", "password": "securepass123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Para la regresión vamos directo al CRUD si el endpoint no existe de forma aislada
    from app.crud.crud_user import get_patient
    
    pat_db = await get_patient(db_session, patient.id)
    assert pat_db is not None
    assert pat_db.user.email == "reg_pat@x.com"

@pytest.mark.asyncio
async def test_r6_not_found_handling(client: AsyncClient):
    # R6: Garantizar que la app responde elegantemente con 404 a rutas inexistentes y no arroja 500
    res = await client.get("/api/v1/this-route-does-not-exist")
    assert res.status_code == 404

import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_r2_concurrent_appointments(client: AsyncClient, regression_users):
    # R2: Dos peticiones simultáneas por el mismo slot médico
    res_login = await client.post("/api/v1/auth/login", data={"username": "reg_pat@x.com", "password": "securepass123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
    
    appt_data = {
        "doctor_id": 999,
        "center_id": 999,
        "appointment_date": future_date,
        "notes": "Concurrent R2"
    }
    
    # Enviar peticiones simultáneas
    results = await asyncio.gather(
        client.post("/api/v1/appointments/", json=appt_data, headers=headers),
        client.post("/api/v1/appointments/", json=appt_data, headers=headers),
        client.post("/api/v1/appointments/", json=appt_data, headers=headers)
    )
    
    for res in results:
        # Should be gracefully rejected (404/422/400) or accepted (201), but NEVER a 500 Internal Server Error DB crash
        assert res.status_code < 500, "Concurrency caused a Server Error"

@pytest.mark.asyncio
async def test_r3_sql_injection_chatbot(client: AsyncClient, regression_users):
    # R3: Intento de inyección SQL en búsqueda de chatbot
    res_login = await client.post("/api/v1/auth/login", data={"username": "reg_pat@x.com", "password": "securepass123"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "history": [],
        "message": "Encuentra doctores donde 1=1; DROP TABLE users; --"
    }
    
    # Burlamos la llamada al LLM para testear solo la infraestructura de nuestra API
    with patch("app.services.chat_service.ChatGoogleGenerativeAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Entiendo, buscas un doctor.")
        res = await client.post("/api/v1/chat/", json=payload, headers=headers)
        
    # The API should parse this as normal text and not crash the DB
    assert res.status_code == 200
    assert "response" in res.json()
