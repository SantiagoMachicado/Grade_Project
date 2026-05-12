import pytest
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError
from app.schemas.user import UserCreate, RoleEnum
from app.schemas.appointment import AppointmentCreate

# U1: Validar creación de Patient con correo válido
def test_u1_create_patient_valid_email():
    patient_data = {
        "email": "test@patient.com",
        "role": RoleEnum.PATIENT,
        "password": "securepassword123",
        "full_name": "Test Patient"
    }
    user = UserCreate(**patient_data)
    assert user.email == "test@patient.com"
    assert user.role == RoleEnum.PATIENT

# U2: FastAPI debe rechazar automáticamente un POST con un email inválido (reglas de Pydantic)
def test_u2_reject_invalid_email():
    patient_data = {
        "email": "not-an-email",
        "role": RoleEnum.PATIENT,
        "password": "securepassword123",
        "full_name": "Test Patient"
    }
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**patient_data)
    assert "value is not a valid email address" in str(exc_info.value)

# U3: Crear entidad Appointment en memoria (Schema) asegurando timestamps
def test_u3_create_appointment_memory():
    future_date = datetime.now(timezone.utc) + timedelta(days=2)
    appt_data = {
        "appointment_date": future_date,
        "doctor_id": 1,
        "center_id": 1,
        "notes": "Test appointment"
    }
    appt = AppointmentCreate(**appt_data)
    assert appt.doctor_id == 1
    assert appt.center_id == 1
    assert appt.notes == "Test appointment"
    assert appt.appointment_date == future_date

# U4: Validar que el AppointmentCreate acepte fechas en el futuro
def test_u4_appointment_accepts_future_date():
    future_date = datetime.now(timezone.utc) + timedelta(days=5)
    appt_data = {
        "appointment_date": future_date,
        "doctor_id": 1,
        "center_id": 1
    }
    # No debería arrojar excepción
    appt = AppointmentCreate(**appt_data)
    assert appt.appointment_date == future_date

# U5: FastAPI debe rechazar automáticamente un AppointmentCreate con fecha en el pasado
def test_u5_appointment_rejects_past_date():
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    appt_data = {
        "appointment_date": past_date,
        "doctor_id": 1,
        "center_id": 1
    }
    with pytest.raises(ValidationError) as exc_info:
        AppointmentCreate(**appt_data)
    assert "date" in str(exc_info.value).lower() or "past" in str(exc_info.value).lower()

