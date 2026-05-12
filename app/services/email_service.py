import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_notification_email(to_email: str, subject: str, body: str):
    """
    Sends an email notification.
    If SMTP_PASSWORD is not configured, it simulates the sending by printing it to the console.
    """
    if not settings.SMTP_PASSWORD:
        print("="*50)
        print("SIMULACIÓN DE CORREO (SMTP_PASSWORD no configurado en .env)")
        print(f"Para: {to_email}")
        print(f"Asunto: {subject}")
        print(f"Cuerpo:\n{body}")
        print("="*50)
        return

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        # Login
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        # Send
        server.send_message(msg)
        server.quit()
        print(f"Correo enviado a {to_email}")
    except Exception as e:
        print(f"Error al enviar correo a {to_email}: {e}")
