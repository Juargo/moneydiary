from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Formato de conexión: postgresql://usuario:contraseña@servidor:puerto/base_de_datos
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://moneydiary:moneydiary_password@db:5432/moneydiary"
)

# Para SQLAlchemy 1.4+ con asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base

# La URL para conexiones asíncronas necesita "postgresql+asyncpg://" en lugar de "postgresql://"
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Motor asíncrono
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",  # Consultas SQL en logs en modo DEBUG
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Reciclar conexiones cada 30 min
)

# Sesión asíncrona
async_session = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

# Función para obtener sesión asíncrona
async def get_async_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Motor síncrono (para migraciones o scripts)
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

# Sesión síncrona
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener sesión síncrona
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
