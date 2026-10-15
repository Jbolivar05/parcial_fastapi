"""
Configuración centralizada de la aplicación.

Lee las variables definidas en el archivo .env y las expone
a través del objeto `settings`, para no repetir os.getenv()
por todo el proyecto.
"""
import os

from dotenv import load_dotenv

# Carga las variables del archivo .env al entorno del proceso
load_dotenv()


class Settings:
    """Contenedor de la configuración de la aplicación."""

    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # OTP (máximo 15 minutos según el parcial)
    OTP_EXPIRE_MINUTES: int = int(os.getenv("OTP_EXPIRE_MINUTES", "15"))

    # SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")

    # Solo desarrollo: muestra el OTP en la terminal en vez de enviarlo
    DEV_PRINT_OTP: bool = os.getenv("DEV_PRINT_OTP", "false").lower() == "true"

    def validate(self) -> None:
        """Verifica que las variables críticas estén configuradas.

        Raises:
            RuntimeError: si falta la SECRET_KEY.
        """
        if not self.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY no está definida. Configúrala en el archivo .env"
            )


settings = Settings()
settings.validate()