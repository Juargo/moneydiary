import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Importar configuraciones de base de datos
from .db_config import (
    DATABASE_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    get_database_url, debug_print
)

# Puedes exportar estas variables para que otros módulos puedan acceder a ellas
__all__ = [
    'DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER',
    'engine', 'SessionLocal', 'Base', 'get_db'
]

# Opciones del engine para mejor rendimiento y robustez
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 5}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()