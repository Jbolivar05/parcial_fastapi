"""Endpoints de autenticación."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.middleware import get_current_session, get_current_user
from app.models import LoginSession, User
from app.rate_limiter import limiter
from app.schemas import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResendOTPRequest,
    TokenResponse,
    UserProfile,
    VerifyOTPRequest,
)
from app.security import (
    create_access_token,
    hash_password,
    hash_value,
    verify_password,
)
from app.services.email_service import EmailSendError, send_otp_email
from app.services.otp_service import create_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _get_user_by_email(db: Session, email: str):
    """Busca un usuario por correo (normalizado a minúsculas)."""
    return db.query(User).filter(User.email == email.lower()).first()


def _send_new_otp(db: Session, user: User) -> None:
    """Genera un OTP y lo envía por correo; responde 503 si el envío falla."""
    code = create_otp(db, user)
    try:
        send_otp_email(user.email, code)
    except EmailSendError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo enviar el código. Intenta más tarde.",
        )


def _issue_token(db: Session, user: User) -> TokenResponse:
    """Crea un JWT y registra su sesión en login_sessions."""
    token, expires_at = create_access_token(user.id)
    db.add(
        LoginSession(user_id=user.id, token=hash_value(token), expires_at=expires_at)
    )
    db.commit()
    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/register", response_model=UserProfile, status_code=201)
@limiter.limit("10/minute")
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario (contraseña guardada con bcrypt)."""
    if _get_user_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya está registrado")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya está registrado")
    db.refresh(user)
    return user


@router.post("/login", response_model=MessageResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    """Valida credenciales y envía un OTP por correo (aún sin JWT)."""
    user = _get_user_by_email(db, payload.email)
    # Mismo mensaje para usuario inexistente o clave errónea
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")

    _send_new_otp(db, user)
    return MessageResponse(message="Código enviado a tu correo")


@router.post("/verify-otp", response_model=TokenResponse)
@limiter.limit("5/minute")
def verify_otp_endpoint(
    request: Request, payload: VerifyOTPRequest, db: Session = Depends(get_db)
):
    """Verifica el OTP y entrega el JWT."""
    user = _get_user_by_email(db, payload.email)
    if user is None or not verify_otp(db, user, payload.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Código inválido o expirado")
    return _issue_token(db, user)


@router.post("/resend-otp", response_model=MessageResponse)
@limiter.limit("3/minute")
def resend_otp(
    request: Request, payload: ResendOTPRequest, db: Session = Depends(get_db)
):
    """Reenvía un OTP nuevo. Responde igual exista o no el correo."""
    user = _get_user_by_email(db, payload.email)
    if user is not None:
        _send_new_otp(db, user)
    return MessageResponse(message="Si el correo existe, se envió un nuevo código")


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    user: User = Depends(get_current_user),
    session: LoginSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Emite un JWT nuevo y revoca el anterior."""
    db.delete(session)
    db.commit()
    return _issue_token(db, user)


@router.post("/logout", response_model=MessageResponse)
def logout(
    session: LoginSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    """Cierra sesión: borra la sesión y el token queda revocado."""
    db.delete(session)
    db.commit()
    return MessageResponse(message="Sesión cerrada")