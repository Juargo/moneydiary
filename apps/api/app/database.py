import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Debug helper
def debug_print(message):
    print(message, file=sys.stderr, flush=True)

# Obtener variables de entorno o usar valores predeterminados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")  # Cambia a 5432 que es el puerto por defecto
DB_NAME = os.getenv("DB_NAME", "moneydiary")
DB_USER = os.getenv("DB_USER", "moneydiary_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "moneydiary_password")

# Construir la URL de conexión
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
debug_print(f"Attempting to connect to database: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

# Opciones del engine para mejor rendimiento y robustez
engine = create_engine(
    DATABASE_URL,
    echo=True,             # Enable SQL logging for debugging
    pool_pre_ping=True,    # Verifica que las conexiones están vivas
    pool_size=5,           # Reducir el tamaño del pool para desarrollo
    max_overflow=10,       # Reducir conexiones adicionales
    connect_args={
        "connect_timeout": 5  # Timeout de 5 segundos para conexiones 
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()