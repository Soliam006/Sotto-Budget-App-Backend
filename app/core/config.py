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
        Esta clase trata de encapsular las variables de entorno y la configuracion del backend
    """

    def get_env_file() -> str:
        """
            Check default locations for .env configuration file
            :return: configuration file
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

    APP_NAME: str = "UnSet"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "user"
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None

    # TODO: SECRET_KEY, TOKEN_EXPIRE_TIME variables del .env
    # Token creation
    # 60 minutes * 24 hours * 2 days = 2 days
    TOKEN_EXPIRE_TIME: int = 60 * 24 * 2
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Parameters for the tests
    EMAIL_TEST_USER: str = "test@example.com"
    USERNAME_TEST_USER: str = "test_user"
    FIRST_NAME_TEST_USER: str = "test"
    LAST_NAME_TEST_USER: str = "test"
    PASSWORD_TEST_USER: str = "password"

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_URI(self) -> MySQLDsn:

        database_uri = MultiHostUrl.build(
            scheme="mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )

        return database_uri


settings = Settings()