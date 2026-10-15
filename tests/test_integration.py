"""Pruebas de integración del flujo completo."""

USER = {"email": "ana@ejemplo.com", "password": "ClaveSegura123", "full_name": "Ana Gómez"}


def _login_and_get_token(client, sent_codes) -> str:
    """Registra al usuario, hace login, verifica el OTP y devuelve el JWT."""
    client.post("/auth/register", json=USER)
    client.post("/auth/login", json={"email": USER["email"], "password": USER["password"]})
    r = client.post(
        "/auth/verify-otp", json={"email": USER["email"], "code": sent_codes[-1]}
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def test_full_flow_register_login_otp_profile(client, sent_codes):
    """Verifica el flujo completo: registro, login, OTP y consulta del perfil."""
    token = _login_and_get_token(client, sent_codes)
    r = client.get("/users/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == USER["email"]


def test_protected_route_without_token_returns_401(client):
    """Verifica que una ruta protegida sin token responde 401."""
    assert client.get("/users/profile").status_code == 401


def test_logout_revokes_token(client, sent_codes):
    """Verifica que después del logout el mismo token ya no es válido."""
    token = _login_and_get_token(client, sent_codes)
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/users/profile", headers=headers).status_code == 401


def test_wrong_otp_is_rejected(client, sent_codes):
    """Verifica que un código OTP incorrecto responde 400."""
    client.post("/auth/register", json=USER)
    client.post("/auth/login", json={"email": USER["email"], "password": USER["password"]})
    r = client.post("/auth/verify-otp", json={"email": USER["email"], "code": "000000"})
    assert r.status_code == 400


def test_duplicate_register_returns_409(client):
    """Verifica que registrar dos veces el mismo correo responde 409."""
    client.post("/auth/register", json=USER)
    assert client.post("/auth/register", json=USER).status_code == 409