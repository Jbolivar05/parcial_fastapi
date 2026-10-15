"""Funciones de seguridad: contraseñas, JWT y HMAC."""
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de una contraseña."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Compara una contraseña con su hash bcrypt."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def hash_value(value: str) -> str:
    """HMAC-SHA256 con la SECRET_KEY. Se usa para guardar OTPs y tokens."""
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"), value.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def create_access_token(user_id: int) -> Tuple[str, datetime]:
    """Crea un JWT con claim de expiración.

    Returns:
        (token, fecha_de_expiración_en_UTC_sin_zona)
    """
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "exp": expires,  # claim de expiración
        "iat": datetime.now(timezone.utc),
        "jti": uuid.uuid4().hex,  # id único: dos tokens nunca son iguales
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expires.replace(tzinfo=None)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica y valida un JWT. Devuelve None si es inválido o expiró."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError:
        return None