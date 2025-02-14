from sqlmodel import Session, create_engine, SQLModel
from app.core.config import settings

# 🛠 Creamos el engine con la configuración correcta (local o Railway)
engine = create_engine(str(settings.SQLALCHEMY_URI), echo=True)

def get_session():
    """Generador de sesiones para SQLModel."""
    with Session(engine) as session:
        yield session

# 🔹 Crear automáticamente las tablas al iniciar la aplicación
def init_db():
    SQLModel.metadata.create_all(engine)
