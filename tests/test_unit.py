"""Pruebas unitarias."""
from datetime import timedelta

from app.models import OTPCode, User, utcnow
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.services.otp_service import create_otp, generate_code, verify_otp


def _make_user(db) -> User:
    """Crea y guarda un usuario de prueba en la base de datos."""
    user = User(email="t@t.com", password_hash=hash_password("Clave12345"), full_name="Test")
    db.add(user)
    db.commit()
    return user


def test_password_hash_is_not_plain():
    """Verifica que la contraseña no se guarda en texto plano."""
    assert hash_password("Clave12345") != "Clave12345"


def test_password_verification():
    """Verifica que la clave correcta pasa y la incorrecta se rechaza."""
    h = hash_password("Clave12345")
    assert verify_password("Clave12345", h) is True
    assert verify_password("otra", h) is False


def test_jwt_roundtrip():
    """Verifica que un JWT creado se decodifica con sus claims sub y exp."""
    token, _ = create_access_token(7)
    payload = decode_access_token(token)
    assert payload["sub"] == "7"
    assert "exp" in payload


def test_jwt_invalid_returns_none():
    """Verifica que un token falso devuelve None."""
    assert decode_access_token("token.falso.xyz") is None


def test_otp_has_six_digits():
    """Verifica que el OTP generado tiene 6 caracteres numéricos."""
    code = generate_code()
    assert len(code) == 6 and code.isdigit()


def test_otp_valid_then_used_cannot_repeat(db):
    """Verifica que un OTP sirve una sola vez y la segunda verificación falla."""
    user = _make_user(db)
    code = create_otp(db, user)
    assert verify_otp(db, user, code) is True
    assert verify_otp(db, user, code) is False


def test_otp_expired_is_rejected(db):
    """Verifica que un OTP vencido es rechazado."""
    user = _make_user(db)
    code = create_otp(db, user)
    otp = db.query(OTPCode).first()
    otp.expires_at = utcnow() - timedelta(minutes=1)
    db.commit()
    assert verify_otp(db, user, code) is False