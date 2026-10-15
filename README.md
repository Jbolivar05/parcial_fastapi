# Sistema de Autenticación con OTP - FastAPI

API de autenticación con doble factor: el usuario inicia sesión con correo y
contraseña, recibe un código OTP de 6 dígitos por correo y, al verificarlo,
obtiene un token JWT para acceder a rutas protegidas.

**Equipo:** Javier Bolivar
**Despliegue:** (pendiente)
**Documentación interactiva:** (pendiente)

## Tecnologías

- FastAPI (Python 3.9+)
- SQLAlchemy + SQLite
- PyOTP (generación de OTP)
- PyJWT (tokens) y bcrypt (contraseñas)
- smtplib (envío de correo)
- SlowAPI (rate limiting)
- Pytest (pruebas)

## Instalación

1. Clonar el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
cd parcial_fastapi
```

2. Crear el entorno virtual:

```bash
python -m venv venv
```

3. Activar el entorno virtual.

En Windows:

```bash
venv\Scripts\activate
```

En Mac/Linux:

```bash
source venv/bin/activate
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

5. Crear el archivo `.env` a partir de `.env.example` y completar los valores.
   Para generar la clave secreta:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

6. Ejecutar el servidor:

```bash
uvicorn app.main:app --reload
```

7. Abrir `http://127.0.0.1:8000/docs` para probar la API.

## Variables de entorno

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | URL de la base de datos (por defecto `sqlite:///./app.db`) |
| `SECRET_KEY` | Clave secreta para firmar JWT y proteger OTP/tokens |
| `ALGORITHM` | Algoritmo del JWT (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del JWT en minutos |
| `OTP_EXPIRE_MINUTES` | Validez del OTP en minutos (máximo 15) |
| `SMTP_HOST` / `SMTP_PORT` | Servidor SMTP (Gmail: `smtp.gmail.com` / `587`) |
| `SMTP_USER` / `SMTP_PASSWORD` | Credenciales SMTP (en Gmail, contraseña de aplicación) |
| `EMAIL_FROM` | Remitente de los correos |

## Endpoints

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/auth/register` | Registrar usuario | No |
| POST | `/auth/login` | Validar credenciales y enviar OTP | No |
| POST | `/auth/verify-otp` | Verificar OTP y obtener JWT | No |
| POST | `/auth/resend-otp` | Reenviar OTP | No |
| POST | `/auth/refresh` | Emitir JWT nuevo y revocar el anterior | Sí |
| POST | `/auth/logout` | Cerrar sesión y revocar token | Sí |
| GET | `/users/profile` | Ver perfil | Sí |
| PUT | `/users/profile` | Actualizar perfil | Sí |

## Flujo de autenticación

1. `POST /auth/register` crea la cuenta.
2. `POST /auth/login` valida la contraseña y envía el OTP por correo.
3. `POST /auth/verify-otp` valida el código y devuelve el JWT.
4. Las rutas protegidas se llaman con el header `Authorization: Bearer <token>`.

## Seguridad

- Contraseñas hasheadas con bcrypt.
- OTP de 6 dígitos, válido máximo 15 minutos y de un solo uso.
- OTP y tokens se almacenan como HMAC-SHA256, nunca en texto plano.
- JWT con claim de expiración; cada token se registra en `login_sessions`.
- El logout elimina la sesión, por lo que el token queda revocado.
- Rate limiting: login 5/min, verify-otp 5/min, resend-otp 3/min, register 10/min.
- Mensajes de error genéricos que no revelan si un correo existe.
- Los errores internos no exponen información sensible.

## Pruebas

```bash
pytest -v
```

Incluye 7 pruebas unitarias y 5 de integración.

## Despliegue

El proyecto incluye `requirements.txt` y `Procfile`. Comando de arranque:

```bash
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

Configurar en la plataforma las mismas variables del `.env`.

## Estructura

```
app/
├── config.py
├── database.py
├── models.py
├── schemas.py
├── security.py
├── middleware.py
├── rate_limiter.py
├── main.py
├── routes/
│   ├── auth.py
│   └── users.py
└── services/
    ├── otp_service.py
    └── email_service.py
tests/
├── conftest.py
├── test_unit.py
└── test_integration.py
```

## Contribuciones

| Integrante | Parte desarrollada |
|---|---|
| Javier Bolivar | Proyecto completo: configuración, base de datos, modelos, esquemas, seguridad, middleware, rate limiting, servicios de OTP y correo, rutas, pruebas y despliegue |