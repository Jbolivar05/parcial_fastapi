"""Envío de correos con smtplib."""
import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


class EmailSendError(Exception):
    """Se lanza cuando no se pudo enviar el correo."""


def send_otp_email(to_email: str, code: str) -> None:
    """Envía el código OTP al correo indicado.

    Raises:
        EmailSendError: si el SMTP falla o no está configurado.
    """
    if settings.DEV_PRINT_OTP:
        print(f"[DEV] OTP para {to_email}: {code}", flush=True)
        return

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.error("SMTP no configurado")
        raise EmailSendError("Servicio de correo no configurado")

    msg = EmailMessage()
    msg["Subject"] = "Tu código de verificación"
    msg["From"] = settings.EMAIL_FROM or settings.SMTP_USER
    msg["To"] = to_email
    msg.set_content(
        f"Tu código de verificación es: {code}\n\n"
        f"Es válido por {settings.OTP_EXPIRE_MINUTES} minutos. "
        "Si no lo solicitaste, ignora este mensaje."
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Fallo al enviar correo: %s", type(exc).__name__)
        raise EmailSendError("No se pudo enviar el correo") from exc