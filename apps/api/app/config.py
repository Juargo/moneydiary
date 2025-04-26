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
    # Campos con anotaciones de tipo apropiadas
    ALLOWED_HOSTS_RAW: str = "localhost,127.0.0.1"
    ENVIRONMENT: str = Field(default="development")
    
    # Otras configuraciones que podrías necesitar
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(default="default-insecure-key")
    CORS_ORIGINS: str = Field(default="http://localhost:3000")

    # OAuth2 Google settings
    google_client_id: str = Field(default="")
    google_client_secret: str = Field(default="")
    google_redirect_uri: str = Field(default="http://localhost:8000/api/v1/auth/google/callback")
    google_auth_scopes: str = Field(default="openid email profile")
    
    # Frontend application settings
    frontend_url: str = Field(default="http://localhost:3000")
    frontend_auth_callback_path: str = Field(default="/auth/callback")
    frontend_auth_error_path: str = Field(default="/auth/error")
    
    # JWT settings
    jwt_secret_key: str = Field(default="")  # Mejor no usar SECRET_KEY por defecto
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)
    
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
    
    # Property para JWT secret más seguro
    @property
    def get_jwt_secret(self) -> str:
        if not self.jwt_secret_key:
            if self.ENVIRONMENT == "production":
                raise ValueError("JWT Secret key must be set in production environment!")
            return self.SECRET_KEY
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
    return Settings()

settings = get_settings()