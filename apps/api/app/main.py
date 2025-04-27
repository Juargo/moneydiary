# FastAPI
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import text

# Imports internos
from .db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER
from .database import engine, Base, get_db
from .config import settings
from contextlib import asynccontextmanager

# Importamos todos los modelos de una vez
from .models import *

# Versión
VERSION = "0.1.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Create configuration dictionary excluding sensitive information
    config_dict = {
        "VERSION": VERSION,
        "ENVIRONMENT": settings.ENVIRONMENT,
        "DEBUG": settings.DEBUG,
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
        "CORS_ORIGINS": settings.CORS_ORIGINS_LIST,
        "DATABASE_URL": "postgresql://{user}:****@{host}:{port}/{database}".format(
            user=DB_USER, host=DB_HOST, port=DB_PORT, database=DB_NAME
        ),
        "google_auth_scopes": settings.GOOGLE_AUTH_SCOPES_LIST,
        "frontend_url": settings.frontend_url,
        "frontend_auth_callback_path": settings.frontend_auth_callback_path,
        "frontend_auth_error_path": settings.frontend_auth_error_path,
    }
    
    # Print configuration to logs
    print(f"\n{'='*50}\nMoneyDiary API v{VERSION} starting with configuration:\n")
    for key, value in config_dict.items():
        print(f"{key}: {value}")
    print(f"{'='*50}\n")
    
    # Startup code finished, yield control back to FastAPI
    yield
    # Shutdown code would go here (if needed in the future)

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

@app.get("/")
async def root():
    return {
        "message": f"MoneyDiary API v{VERSION}",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "graphql_endpoint": "/graphql",
        "api_endpoint": "/api"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = {
            "error": str(e),
            "connection_url": f"postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME,
            "user": DB_USER
        }
    
    return {
        "status": "ok" if db_status == "ok" else "error",
        "version": VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }

# Include routes (commented out until implemented)
# app.include_router(api_router, prefix="/api")
