import pytest
from datetime import datetime, timedelta, timezone, date, time
from app.core import security
from app.crud.crud_user import create_user
from app.crud.crud_clinic import create_medical_center, create_schedule
from app.crud.crud_appointment import get_doctor_stats, get_doctor_dashboard_stats, get_doctor_agenda
from app.models.user import RoleEnum
from app.models.clinic import MedicalCenter, Schedule, DoctorMedicalCenter
from app.models.appointment import Appointment, AppointmentStatusEnum
from app.schemas.user import UserCreate
from app.schemas.clinic import MedicalCenterCreate, ScheduleCreate
from sqlalchemy import insert

# U18 y U19: Funciones de seguridad de contraseñas (Passlib/Bcrypt)
def test_u18_u19_password_hashing():
    plain_password = "supersecretpassword123"
    hashed = security.get_password_hash(plain_password)
    
    # U18: El hash debe ser diferente al texto plano
    assert hashed != plain_password
    assert len(hashed) > 10
    
    # U19: Verificación exitosa vs fallida
    assert security.verify_password(plain_password, hashed) is True
    assert security.verify_password("wrongpassword", hashed) is False

import pytest_asyncio

# Pruebas asíncronas para lógica de Negocio usando la BD (Estadísticas y Agendas)
@pytest_asyncio.fixture
async def sample_doctor(db_session):
    # Crear un doctor de prueba
    doc_schema = UserCreate(
        email="testdoc_stats@test.com", password="securepass123", role=RoleEnum.DOCTOR,
        full_name="Dr. Stats", specialty="General", license_number="123", consultation_fee=100.0
    )
    doc_user = await create_user(db_session, doc_schema)
    return doc_user.id

@pytest.mark.asyncio
async def test_u13_doctor_stats_zero_division(db_session, sample_doctor):
    # U13: get_doctor_stats debe retornar 0% y no dividir por cero si no tiene citas
    stats = await get_doctor_stats(db_session, sample_doctor)
    
    assert stats["breakdown"]["completed_pct"] == 0
    assert stats["breakdown"]["cancelled_pct"] == 0
    assert stats["breakdown"]["absent_pct"] == 0
    assert stats["total_active_patients"] == 0
    assert stats["total_revenue"] == 0.0

@pytest.mark.asyncio
async def test_u14_doctor_stats_revenue(db_session, sample_doctor):
    # U14: Crear 3 citas completadas y verificar ingresos
    now = datetime.now()
    
    # Crear pacientes falsos (necesitan IDs ficticios o reales para patient_id)
    # Por simplicidad, los insertamos directamente si la BD lo permite, pero mejor crearlos por crud
    patient1 = await create_user(db_session, UserCreate(email="p1@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="P1"))
    patient2 = await create_user(db_session, UserCreate(email="p2@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="P2"))
    
    appts = [
        Appointment(doctor_id=sample_doctor, patient_id=patient1.id, center_id=1, schedule_id=1, appointment_date=now, status="completada"),
        Appointment(doctor_id=sample_doctor, patient_id=patient2.id, center_id=1, schedule_id=1, appointment_date=now, status="completada"),
        Appointment(doctor_id=sample_doctor, patient_id=patient1.id, center_id=1, schedule_id=1, appointment_date=now, status="completada"),
        Appointment(doctor_id=sample_doctor, patient_id=patient2.id, center_id=1, schedule_id=1, appointment_date=now, status="cancelada")
    ]
    db_session.add_all(appts)
    await db_session.commit()
    
    stats = await get_doctor_stats(db_session, sample_doctor)
    
    # 3 citas completadas * 100 de fee = 300
    assert stats["total_revenue"] == 300.0
    assert stats["breakdown"]["completed_pct"] == 75 # 3 de 4 terminaron
    assert stats["breakdown"]["cancelled_pct"] == 25 # 1 de 4 se canceló

@pytest.mark.asyncio
async def test_u15_doctor_dashboard_new_patients(db_session, sample_doctor):
    now = datetime.now()
    patient_old = await create_user(db_session, UserCreate(email="po@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="PO"))
    patient_new = await create_user(db_session, UserCreate(email="pn@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="PN"))
    
    # Cita vieja hace 1 mes
    db_session.add(Appointment(doctor_id=sample_doctor, patient_id=patient_old.id, center_id=1, schedule_id=1, appointment_date=now - timedelta(days=30), status="completada"))
    # Cita nueva de ese mismo paciente viejo (no debe contar como nuevo)
    db_session.add(Appointment(doctor_id=sample_doctor, patient_id=patient_old.id, center_id=1, schedule_id=1, appointment_date=now, status="completada"))
    
    # Cita nueva de paciente nuevo
    db_session.add(Appointment(doctor_id=sample_doctor, patient_id=patient_new.id, center_id=1, schedule_id=1, appointment_date=now - timedelta(days=2), status="completada"))
    
    await db_session.commit()
    
    dash = await get_doctor_dashboard_stats(db_session, sample_doctor)
    # Sólo 'patient_new' es nuevo en los últimos 7 días
    assert dash["new_patients_count"] == 1

@pytest.mark.asyncio
async def test_u16_u17_doctor_agenda_slots(db_session, sample_doctor):
    # U16: Fraccionamiento correcto de slots (ej. 8:00 a 10:00 -> 4 slots)
    center = await create_medical_center(db_session, MedicalCenterCreate(name="Centro Test", address="123", phone="123"))
    
    # Asignar doctor al centro manualmente
    doc_center = DoctorMedicalCenter(doctor_id=sample_doctor, center_id=center.id)
    db_session.add(doc_center)
    await db_session.commit()
    await db_session.refresh(doc_center)
    
    target_date = date.today() + timedelta(days=(7 - date.today().weekday())) # Próximo lunes
    dow = target_date.weekday()
    
    # Crear horario (8:00 a 10:00)
    sched = ScheduleCreate(assignment_id=doc_center.id, day_of_week=dow, start_time=time(8, 0), end_time=time(10, 0), is_available=True)
    await create_schedule(db_session, sched)
    
    # Consultar agenda sin citas
    target_date_str = target_date.strftime("%Y-%m-%d")
    slots = await get_doctor_agenda(db_session, sample_doctor, target_date_str)
    
    # Debe haber 4 slots: 8:00, 8:30, 9:00, 9:30
    assert len(slots) == 4
    assert slots[0].time == "08:00"
    assert slots[-1].time == "09:30"
    assert all(s.type.value == "available" for s in slots)
    
    # U17: Crear una cita cancelada a las 09:00, el slot debe seguir AVAILABLE
    patient = await create_user(db_session, UserCreate(email="px@x.com", password="securepass123", role=RoleEnum.PATIENT, full_name="PX"))
    dt_9am = datetime.combine(target_date, time(9, 0))
    appt_cancelled = Appointment(doctor_id=sample_doctor, patient_id=patient.id, center_id=center.id, schedule_id=1, appointment_date=dt_9am, status="cancelada")
    db_session.add(appt_cancelled)
    await db_session.commit()
    
    slots_with_cancelled = await get_doctor_agenda(db_session, sample_doctor, target_date_str)
    
    # El slot de las 09:00 (índice 2) debe ser AVAILABLE porque la cita está cancelada
    assert slots_with_cancelled[2].time == "09:00"
    assert slots_with_cancelled[2].type.value == "available"

@pytest.mark.asyncio
async def test_u20_create_medical_center_wkt(db_session):
    # U20: Transformación correcta de location_wkt
    schema = MedicalCenterCreate(name="Clinica Geo", address="C1", location_wkt="POINT(-68.1193 -16.4897)", phone="111")
    center = await create_medical_center(db_session, schema)
    
    # Verificar que el SRID se insertó correctamente y la BD devolvió un objeto WKBElement
    assert center.location is not None
    assert type(center.location).__name__ == "WKBElement"
