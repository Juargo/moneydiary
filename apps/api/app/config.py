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
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()