import os
import secrets

from pydantic import (
    MySQLDsn,
    computed_field
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
        Esta clase encapsula las variables de entorno y configuración del backend.
    """

    def get_env_file() -> str:
        """
            Busca el archivo .env en las ubicaciones predeterminadas.
            :return: ruta del archivo .env
        """
        top_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '.env')
        if os.path.exists('.env'):
            env_file = '.env'
        elif os.path.exists(top_path):
            env_file = top_path
        else:
            env_file = '.env'

        return env_file

    model_config = SettingsConfigDict(
        env_file=get_env_file(), env_ignore_empty=True, extra="ignore"
    )

    # 🔹 Agregamos la variable ENVIRONMENT
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # Por defecto, "development"

    # Configuración de base de datos
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASSWORD: str | None = os.getenv("DB_PASSWORD", None)
    DB_NAME: str | None = os.getenv("DB_NAME", None)

    # 🔹 Configuración para Railway (Producción)
    DATABASE_URL: str | None = os.getenv("DATABASE_URL", None)

    # Configuración del token
    TOKEN_EXPIRE_TIME: int = 60 * 24 * 2  # 2 días
    SECRET_KEY: str = secrets.token_urlsafe(32)

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_URI(self) -> MySQLDsn:
        """
        Construye la URL de conexión a la base de datos en función del entorno.
        """
        if self.ENVIRONMENT == "production" and self.DATABASE_URL:
            return self.DATABASE_URL  # Usar Railway en producción

        # Si no estamos en producción, usamos la configuración local
        database_uri = MultiHostUrl.build(
            scheme="mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=f"/{self.DB_NAME}" if self.DB_NAME else "",
        )

        return database_uri


# Instancia global de configuración
settings = Settings()
