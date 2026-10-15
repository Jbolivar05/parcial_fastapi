"""Generación y validación de códigos OTP."""
import hmac
from datetime import timedelta

import pyotp
from sqlalchemy.orm import Session

from app.config import settings
from app.models import OTPCode, User, utcnow
from app.security import hash_value


def generate_code() -> str:
    """Genera un código numérico de 6 dígitos con PyOTP.

    Se usa un secreto aleatorio nuevo en cada llamada, por lo que
    el código es impredecible.
    """
    return pyotp.TOTP(pyotp.random_base32(), digits=6).now()


def create_otp(db: Session, user: User) -> str:
    """Crea un OTP nuevo para el usuario e invalida los anteriores.

    Returns:
        El código en texto plano (solo para enviarlo por correo).
    """
    # Invalida códigos previos que sigan sin usar
    db.query(OTPCode).filter(
        OTPCode.user_id == user.id, OTPCode.used.is_(False)
    ).update({"used": True})

    code = generate_code()
    db.add(
        OTPCode(
            user_id=user.id,
            code=hash_value(code),
            expires_at=utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )
    )
    db.commit()
    return code


def verify_otp(db: Session, user: User, code: str) -> bool:
    """Valida un OTP: debe existir, no estar usado ni vencido.

    Si es válido, lo marca como usado (un solo uso).
    """
    otp = (
        db.query(OTPCode)
        .filter(OTPCode.user_id == user.id, OTPCode.used.is_(False))
        .order_by(OTPCode.created_at.desc())
        .first()
    )
    if otp is None or otp.expires_at < utcnow():
        return False

    # compare_digest evita ataques por tiempo de comparación
    if not hmac.compare_digest(otp.code, hash_value(code)):
        return False

    otp.used = True
    db.commit()
    return True