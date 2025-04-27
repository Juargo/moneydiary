# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# Imports internos
from .database import engine, Base
from .config import settings
from .lifecycle import lifespan, VERSION  # Import from the lifecycle module
from .routers import basic  # Import the basic router

# Importamos todos los modelos de una vez
from .models import *

# Crear app
app = FastAPI(
    title="MoneyDiary API",
    description="API for the MoneyDiary app",
    version=VERSION,
    lifespan=lifespan
)

# Crear tablas en modo desarrollo (para producción, usar Alembic)
if settings.ENVIRONMENT != "production":
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {e}")
        raise

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(basic.router)

# Additional routers can be included as they are implemented
# app.include_router(api_router, prefix="/api")
