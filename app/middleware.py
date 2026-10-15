"""Validación de tokens JWT para rutas protegidas."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LoginSession, User, utcnow
from app.security import decode_access_token, hash_value

bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token inválido o expirado",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> LoginSession:
    """Valida el JWT y comprueba que su sesión siga activa en la BD.

    Si el usuario hizo logout, la sesión ya no existe y el token se rechaza.
    """
    if credentials is None:
        raise _UNAUTHORIZED

    token = credentials.credentials
    if decode_access_token(token) is None:
        raise _UNAUTHORIZED

    session = (
        db.query(LoginSession)
        .filter(LoginSession.token == hash_value(token))
        .first()
    )
    if session is None or session.expires_at < utcnow():
        raise _UNAUTHORIZED
    return session


def get_current_user(
    session: LoginSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> User:
    """Devuelve el usuario dueño de la sesión activa."""
    user = db.get(User, session.user_id)
    if user is None:
        raise _UNAUTHORIZED
    return user