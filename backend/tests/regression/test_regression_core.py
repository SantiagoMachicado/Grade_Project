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
    assert pat_db.user.email == "reg_pat@x.com" # La relación cargada es crítica

@pytest.mark.asyncio
async def test_r6_not_found_handling(client: AsyncClient):
    # R6: Garantizar que la app responde elegantemente con 404 a rutas inexistentes y no arroja 500
    res = await client.get("/api/v1/this-route-does-not-exist")
    assert res.status_code == 404
