"""Fixtures compartidas de pytest: BD en memoria, cliente y correo falso."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.rate_limiter import limiter

# BD SQLite en memoria, aislada del app.db real
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def disable_rate_limit():
    """Desactiva el rate limiting durante las pruebas."""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
def db():
    """Sesión de BD limpia para cada test."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sent_codes(monkeypatch):
    """Reemplaza el envío de correo y guarda los OTP 'enviados'."""
    codes = []

    def fake_send(to_email, code):
        codes.append(code)

    monkeypatch.setattr("app.routes.auth.send_otp_email", fake_send)
    return codes


@pytest.fixture
def client(db):
    """Cliente de pruebas conectado a la BD de test."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()