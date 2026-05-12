import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

from app.services.email_service import send_notification_email
from app.services.chat_service import get_gemini_response
from app.services.scheduler import check_appointments_and_notify
from app.models.appointment import Appointment
from sqlalchemy import select

# U6: chat_service.py - Simular respuesta con acción de agendar (Mocking LangChain)
@pytest.mark.asyncio
@patch("app.services.chat_service.ChatGoogleGenerativeAI.ainvoke", new_callable=AsyncMock)
async def test_u6_chat_service_agenda_intent(mock_ainvoke, db_session):
    # Simulamos que el LLM decide que es Cardiología
    mock_ainvoke.return_value = MagicMock(content="Te recomiendo un cardiólogo. [ACTION:MAP:Cardiología]")
    
    response = await get_gemini_response([], "Me duele el pecho fuerte", db_session)
    assert "[ACTION:MAP:Cardiología]" in response

# U7: chat_service.py - Información General sin acción
@pytest.mark.asyncio
@patch("app.services.chat_service.ChatGoogleGenerativeAI.ainvoke", new_callable=AsyncMock)
async def test_u7_chat_service_general_info(mock_ainvoke, db_session):
    mock_ainvoke.return_value = MagicMock(content="Hola, ¿en qué te puedo ayudar hoy?")
    
    response = await get_gemini_response([], "Hola", db_session)
    assert "[ACTION:MAP:" not in response
    assert "ayudar hoy" in response

# U8: email_service.py - Generar HTML de notificación correctamente sin error
@patch("app.services.email_service.smtplib.SMTP")
def test_u8_email_service_render(mock_smtp):
    # Simulamos que hay SMTP password para forzar la lógica real
    with patch("app.services.email_service.settings.SMTP_PASSWORD", "mockedpassword"):
        send_notification_email("test@mail.com", "Subject", "<p>HTML Body</p>")
        mock_smtp.assert_called()

# U9: email_service.py - Renderizar sin romper por falta de password (Simulación)
@patch("app.services.email_service.print")
def test_u9_email_service_fallback_no_password(mock_print):
    # Garantizamos que SMTP_PASSWORD sea nulo
    with patch("app.services.email_service.settings.SMTP_PASSWORD", None):
        send_notification_email("test@mail.com", "Asunto Falso", "Cuerpo Falso")
        # El servicio debe hacer fallback a print y no lanzar error
        assert mock_print.called

# U10 y U11: Matemática de fechas indirecta evaluada mediante la inserción de appointments 
# y la verificación del scheduler. (Combinado con U12).
@pytest.mark.asyncio
async def test_u10_u11_u12_scheduler_flags(db_session):
    # Creamos un mock de AsyncSessionLocal que retorna nuestro db_session
    class MockSessionContext:
        async def __aenter__(self):
            return db_session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("app.services.scheduler.AsyncSessionLocal", return_value=MockSessionContext()):
        with patch("app.services.scheduler.send_notification_email") as mock_email:
            # 1. Crear citas de prueba en DB usando el fixture db_session
            now = datetime.now(timezone.utc)
            
            # U10: Cita a ~23 horas (debe notificar 24h)
            appt_24 = Appointment(
                patient_id=None, doctor_id=None, center_id=None, schedule_id=None,
                appointment_date=now + timedelta(hours=23),
                status="confirmada", notified_24h=False, notified_3h=False
            )
            
            # U11: Cita a ~2 horas (debe notificar 3h)
            appt_3 = Appointment(
                patient_id=None, doctor_id=None, center_id=None, schedule_id=None,
                appointment_date=now + timedelta(hours=2),
                status="confirmada", notified_24h=False, notified_3h=False
            )
            
            db_session.add(appt_24)
            db_session.add(appt_3)
            await db_session.commit()
            
            # Ejecutar scheduler
            await check_appointments_and_notify()
            
            # Verificar en DB que las flags cambiaron (U12)
            await db_session.refresh(appt_24)
            await db_session.refresh(appt_3)
            
            assert appt_24.notified_24h is True
            assert appt_24.notified_3h is False # No está a < 3h
            
            assert appt_3.notified_3h is True
            assert appt_3.notified_24h is True # Se marcan ambas por seguridad
