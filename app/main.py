"""
from .core.database import engine
from .models import SQLModel
from .api.main import api_router
from .core.config import settings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging

# Set up logging to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # Optional: also log to console
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

# Allow all origins for simplicity, but you should restrict this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear la base de datos y las tablas
def on_startup():
    SQLModel.metadata.create_all(engine)

app.add_event_handler("startup", on_startup)

app.include_router(api_router)
"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "¡Hola, FastAPI está funcionando!"}
