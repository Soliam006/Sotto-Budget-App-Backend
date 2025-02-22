import os
import secrets
from pydantic import MySQLDsn, computed_field, Field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
        Esta clase encapsula las variables de entorno y configuración del backend.
    """

    APP_NAME: str = "SottoBudget"

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # 🔹 Agregamos la variable ENVIRONMENT
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")  # "development" por defecto

    # Configuración de base de datos
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=3306, env="DB_PORT")
    DB_USER: str = Field(default="user", env="DB_USER")
    DB_PASSWORD: str | None = Field(default=None, env="DB_PASSWORD")
    DB_NAME: str = Field(default="sottobudget", env="DB_NAME")

    # 🔹 Configuración para Railway (Producción)
    DATABASE_URL: str | None = Field(default=None, env="DATABASE_URL")

    # Configuración del token
    TOKEN_EXPIRE_TIME: int = 60 * 24 * 2  # 2 días
    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY", secrets.token_urlsafe(32)), env="SECRET_KEY")

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_URI(self) -> str | None | MultiHostUrl:
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
            path=f"{self.DB_NAME}" if self.DB_NAME else "",
        )

        return database_uri


# Instancia global de configuración
settings = Settings()
