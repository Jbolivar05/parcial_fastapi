"""Esquemas Pydantic de entrada y salida, con ejemplos para /docs."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Datos para registrar un usuario."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    full_name: str = Field(min_length=2, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "vanessa@ejemplo.com",
                "password": "ClaveSegura123",
                "full_name": "Vanessa Pérez",
            }
        }
    )


class LoginRequest(BaseModel):
    """Credenciales para iniciar sesión."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=64)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "vanessa@ejemplo.com", "password": "ClaveSegura123"}
        }
    )


class VerifyOTPRequest(BaseModel):
    """Correo y código OTP de 6 dígitos."""

    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "vanessa@ejemplo.com", "code": "123456"}}
    )


class ResendOTPRequest(BaseModel):
    """Correo al que se reenvía un nuevo OTP."""

    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "vanessa@ejemplo.com"}}
    )


class TokenResponse(BaseModel):
    """Respuesta con el JWT de acceso."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Segundos hasta que expira el token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    )


class MessageResponse(BaseModel):
    """Respuesta simple con un mensaje."""

    message: str

    model_config = ConfigDict(json_schema_extra={"example": {"message": "Operación exitosa"}})


class UserProfile(BaseModel):
    """Perfil público del usuario (nunca incluye el hash)."""

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "vanessa@ejemplo.com",
                "full_name": "Vanessa Pérez",
                "created_at": "2026-09-01T10:00:00",
                "updated_at": "2026-09-01T10:00:00",
            }
        },
    )


class UpdateProfileRequest(BaseModel):
    """Campos editables del perfil (todos opcionales)."""

    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None

    model_config = ConfigDict(
        json_schema_extra={"example": {"full_name": "Vanessa P. Gómez"}}
    )