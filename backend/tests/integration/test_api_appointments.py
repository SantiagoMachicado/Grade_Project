import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone

from app.schemas.user import UserCreate, RoleEnum
from app.crud.crud_user import create_user
from app.models.clinic import MedicalCenter, Schedule, DoctorMedicalCenter
from app.models.appointment import Appointment

import pytest_asyncio

@pytest_asyncio.fixture
async def setup_integration_db(db_session):
    # Setup roles and dependencies for appointments
    p = await create_user(db_session, UserCreate(email="pat_int@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="Patient Int"))
    d = await create_user(db_session, UserCreate(email="doc_int@x.com", password="securepass123", role=RoleEnum.DOCTOR, full_name="Doc Int", specialty="Gen", license_number="123"))
    
    # Clinic
    center = MedicalCenter(name="Center Int", address="Address Int", location="SRID=4326;POINT(-68.1 -16.5)", phone="111")
    db_session.add(center)
    await db_session.commit()
    
    # Assignment
    assignment = DoctorMedicalCenter(doctor_id=d.id, center_id=center.id)
    db_session.add(assignment)
    await db_session.commit()
    
    # Schedule
    from datetime import time
    sched = Schedule(assignment_id=assignment.id, day_of_week=0, start_time=time(8,0), end_time=time(12,0), is_available=True)
    db_session.add(sched)
    await db_session.commit()

    return p, d, center.id, sched.id

@pytest.mark.asyncio
async def test_i3_i4_i5_i10_appointments_flow(client: AsyncClient, setup_integration_db):
    patient, doctor, center_id, sched_id = setup_integration_db
    
    # Login patient
    res_p = await client.post("/api/v1/auth/login", data={"username": "pat_int@x.com", "password": "securepass123"})
    token_p = res_p.json()["access_token"]
    headers_p = {"Authorization": f"Bearer {token_p}"}
    
    # Login doctor
    res_d = await client.post("/api/v1/auth/login", data={"username": "doc_int@x.com", "password": "securepass123"})
    token_d = res_d.json()["access_token"]
    headers_d = {"Authorization": f"Bearer {token_d}"}

    # I3: Create appointment via API
    # El horario configurado es Lunes (0) de 08:00 a 12:00
    now = datetime.now(timezone.utc)
    days_ahead = 0 - now.weekday()
    if days_ahead <= 0: # Target is next week
        days_ahead += 7
    next_monday = now + timedelta(days=days_ahead)
    future_date = next_monday.replace(hour=8, minute=30, second=0, microsecond=0).isoformat()
    
    appt_data = {
        "doctor_id": doctor.id,
        "center_id": center_id,
        "appointment_date": future_date,
        "notes": "Test appointment via API"
    }
    res_create = await client.post("/api/v1/appointments/", json=appt_data, headers=headers_p)
    assert res_create.status_code == 201
    appt_id = res_create.json()["id"]
    
    # I11: Ver en la agenda (Schedule API)
    # Target date to check agenda
    target_date = next_monday.strftime("%Y-%m-%d")
    res_agenda = await client.get(f"/api/v1/appointments/doctor/{doctor.id}/agenda?date={target_date}", headers=headers_p)
    assert res_agenda.status_code == 200
    
    # I4: Reprogram appointment
    future_date2 = next_monday.replace(hour=9, minute=0, second=0, microsecond=0).isoformat()
    appt_data["appointment_date"] = future_date2
    res_update = await client.put(f"/api/v1/appointments/{appt_id}", json=appt_data, headers=headers_p)
    assert res_update.status_code == 200
    assert res_update.json()["appointment_date"] == future_date2.replace("+00:00", "Z")
    
    # I10: PATCH /appointments/{id}/report (Doc ONLY)
    report_data = {"medical_report": "Paciente sano"}
    res_report = await client.patch(f"/api/v1/appointments/{appt_id}/report", json=report_data, headers=headers_d)
    assert res_report.status_code == 200
    
    # I5: Cancel appointment
    res_cancel = await client.delete(f"/api/v1/appointments/{appt_id}", headers=headers_p)
    assert res_cancel.status_code == 204
    
    # I12: 404 Handlers
    res_404 = await client.delete(f"/api/v1/appointments/99999", headers=headers_p)
    assert res_404.status_code == 404
