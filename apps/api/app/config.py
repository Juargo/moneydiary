import os
import json
import sys
from pydantic_settings import BaseSettings
from typing import List, Optional, Union, Any, ClassVar
from functools import lru_cache
from pydantic import Field, computed_field

# Importar la URL de la base de datos desde db_config
from .db_config import DATABASE_URL as DB_URL, debug_print

# Simple function to parse string into list - works with comma-separated or single value
def parse_to_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(value)]

class Settings(BaseSettings):
    # Environment variables without default values - all are required
    ALLOWED_HOSTS_RAW: str
    ENVIRONMENT: str
    DEBUG: bool
    SECRET_KEY: str
    CORS_ORIGINS: str

    # OAuth2 Google settings - all required
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_auth_scopes: str
    
    # Frontend application settings - all required
    frontend_url: str
    frontend_auth_callback_path: str
    frontend_auth_error_path: str
    
    # JWT settings - all required
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int
    
    # Property para computar hosts permitidos
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        hosts = parse_to_list(self.ALLOWED_HOSTS_RAW)
        debug_print(f"DEBUG - Computed ALLOWED_HOSTS: {hosts}")
        return hosts
    
    # Property para computar origenes CORS
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return parse_to_list(self.CORS_ORIGINS)
    
    # Usamos el valor importado directamente
    @property
    def DATABASE_URL(self) -> str:
        debug_print(f"DEBUG - Using DATABASE_URL: {DB_URL}")
        return DB_URL
    
    # Property para JWT secret
    @property
    def get_jwt_secret(self) -> str:
        return self.jwt_secret_key
    
    # Property para obtener Google scopes como lista
    @property
    def GOOGLE_AUTH_SCOPES_LIST(self) -> List[str]:
        return parse_to_list(self.google_auth_scopes)
    
    # Property para construir la URL completa de callback del frontend
    @property
    def FRONTEND_AUTH_SUCCESS_URL(self) -> str:
        return f"{self.frontend_url}{self.frontend_auth_callback_path}"
    
    @property
    def FRONTEND_AUTH_ERROR_URL(self) -> str:
        return f"{self.frontend_url}{self.frontend_auth_error_path}"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

@lru_cache()
def get_settings():
    try:
        return Settings()
    except Exception as e:
        print(f"\n{'='*50}")
        print("ERROR: Missing required environment variables")
        print(f"Please ensure all required variables are defined in the .env file")
        print(f"Error details: {str(e)}")
        print(f"{'='*50}\n")
        sys.exit(1)

settings = get_settings()