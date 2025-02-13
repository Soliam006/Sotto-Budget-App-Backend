from sqlmodel import Session, create_engine, select, SQLModel
from app.core.config import settings
from datetime import datetime

# Creamos el engine conectando con la base de datos.
engine = create_engine(str(settings.SQLALCHEMY_URI))


def get_session():
    with Session(engine) as session:
        yield session

# Crear tablas automáticamente
def init_db():
    SQLModel.metadata.create_all(engine)