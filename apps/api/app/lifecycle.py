from contextlib import asynccontextmanager
from fastapi import FastAPI

# Imports internos
from .db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER
from .config import settings

# Version constant (moved from main.py)
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
