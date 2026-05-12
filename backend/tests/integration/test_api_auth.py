import pytest
from httpx import AsyncClient
from app.schemas.user import UserCreate, RoleEnum
from app.crud.crud_user import create_user

import pytest_asyncio

@pytest_asyncio.fixture
async def create_test_users(db_session):
    # Crear un paciente y un doctor
    p = await create_user(db_session, UserCreate(email="patient_auth@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="Patient"))
    d = await create_user(db_session, UserCreate(email="doc_auth@x.com", password="securepass123", role=RoleEnum.DOCTOR, full_name="Doc", specialty="Gen", license_number="123"))
    a = await create_user(db_session, UserCreate(email="admin_auth@x.com", password="securepass123", role=RoleEnum.ADMIN, full_name="Admin"))
    return p, d, a

@pytest.mark.asyncio
async def test_i6_login_success(client: AsyncClient, create_test_users):
    patient, _, _ = create_test_users
    # I6: Autenticación exitosa
    response = await client.post("/api/v1/auth/login", data={"username": "patient_auth@x.com", "password": "securepass123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_i7_protected_route_unauthorized(client: AsyncClient):
    # I7: Falla sin Authorization header
    response = await client.get("/api/v1/appointments/patient/1")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_i8_i9_rbac_restrictions(client: AsyncClient, create_test_users):
    patient, doctor, admin = create_test_users
    
    # Login paciente
    res_p = await client.post("/api/v1/auth/login", data={"username": "patient_auth@x.com", "password": "securepass123"})
    token_p = res_p.json()["access_token"]
    headers_p = {"Authorization": f"Bearer {token_p}"}
    
    # Login doctor
    res_d = await client.post("/api/v1/auth/login", data={"username": "doc_auth@x.com", "password": "securepass123"})
    token_d = res_d.json()["access_token"]
    headers_d = {"Authorization": f"Bearer {token_d}"}

    # I8: Paciente intentando ver dashboard de doctor (Debe ser 403 Forbidden o 401)
    res = await client.get(f"/api/v1/appointments/doctor/{doctor.id}/dashboard", headers=headers_p)
    assert res.status_code in [403, 401] # Dependiendo de cómo lo hayas implementado en Depends

    # I9: Doctor intentando crear clínicas (Asumimos que solo el Admin puede en /clinics/ POST, o algo similar)
    res_doc_on_patient = await client.get(f"/api/v1/appointments/patient/{patient.id}", headers=headers_d)
    # Un doctor no puede consultar el historial como si fuera el paciente dueño (a menos que no hayas restringido esto, pero según el plan I8 e I9 exigen un 403)
    assert res_doc_on_patient.status_code in [403, 401]
    
    res_doc_create_clinic = await client.post("/api/v1/clinics/", json={"name": "Test", "address": "Test", "phone": "123"}, headers=headers_d)
    assert res_doc_create_clinic.status_code in [403, 401]
