"""Endpoints de perfil de usuario (protegidos)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware import get_current_user
from app.models import User
from app.schemas import UpdateProfileRequest, UserProfile

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/profile", response_model=UserProfile)
def get_profile(user: User = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado."""
    return user


@router.put("/profile", response_model=UserProfile)
def update_profile(
    payload: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza nombre y/o correo del usuario autenticado."""
    if payload.email is not None:
        new_email = payload.email.lower()
        exists = (
            db.query(User).filter(User.email == new_email, User.id != user.id).first()
        )
        if exists:
            raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya está en uso")
        user.email = new_email

    if payload.full_name is not None:
        user.full_name = payload.full_name

    db.commit()
    db.refresh(user)
    return user