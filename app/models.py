"""Modelos SQLAlchemy: users, otp_codes y login_sessions."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow() -> datetime:
    """Fecha/hora actual en UTC (sin zona, para compatibilidad con SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """Usuario registrado en el sistema."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    otp_codes = relationship(
        "OTPCode", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "LoginSession", back_populates="user", cascade="all, delete-orphan"
    )


class OTPCode(Base):
    """Código OTP generado para un usuario (se guarda cifrado con HMAC)."""

    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    code = Column(String(64), nullable=False)  # HMAC del código, no el código plano
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    user = relationship("User", back_populates="otp_codes")


class LoginSession(Base):
    """Sesión activa. Si el token no está aquí, está revocado."""

    __tablename__ = "login_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)  # HMAC del JWT
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    user = relationship("User", back_populates="sessions")