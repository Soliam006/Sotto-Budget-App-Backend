from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from pathlib import Path
from sqlmodel import SQLModel
from app.models.user import *
from alembic import context

# Importa el motor de base de datos y los modelos
from app.core.config import settings

# Esta configuración carga el archivo alembic.ini
config = context.config

# Establece la URL de la base de datos
config.set_main_option('sqlalchemy.url', str(settings.SQLALCHEMY_URI))
print(f"SQLALCHEMY_URI: {settings.SQLALCHEMY_URI}")

# Interpretar el archivo de configuración de logging config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importar el metadata del modelo para usarlo en las migraciones
target_metadata = SQLModel.metadata

# Aquí comienza la configuración para la ejecución de las migraciones

def run_migrations_offline():
    """Ejecuta las migraciones en modo 'offline' (sin conexión a la base de datos)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Ejecuta las migraciones en modo 'online' (con conexión a la base de datos)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()