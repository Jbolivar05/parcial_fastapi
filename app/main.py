"""Punto de entrada de la aplicación FastAPI."""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import Base, engine
from app.rate_limiter import limiter
from app.routes import auth, users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Autenticación con OTP",
    description="API con registro, login, OTP por correo y JWT.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(users.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Error genérico: registra el tipo pero no expone detalles al cliente."""
    logger.error("Error no controlado: %s", type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


@app.get("/", tags=["Estado"])
def health():
    """Verifica que la API esté en línea."""
    return {"status": "ok"}