import os
import json
import sys
from pydantic_settings import BaseSettings
from typing import List, Optional, Union, Any, ClassVar
from functools import lru_cache
from pydantic import Field, computed_field
from .database import DATABASE_URL as DB_URL  # Renombra la importación para evitar conflictos

# Debug helper to print to stderr where it will always be visible
def debug_print(message):
    print(message, file=sys.stderr, flush=True)

debug_print("Starting config.py module load")

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
    # Eliminamos DATABASE_URL de los campos base para evitar conflictos
    
    # Otras configuraciones que podrías necesitar
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(default="default-insecure-key")
    CORS_ORIGINS: str = Field(default="http://localhost:3000")
    
    # Property para computar hosts permitidos
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        debug_print(f"DEBUG - Computing ALLOWED_HOSTS from raw value: {repr(self.ALLOWED_HOSTS_RAW)}")
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
        debug_print(f"DEBUG - DATABASE_URL: {DB_URL}")
        return DB_URL
    
    @property
    def SECRET_KEY(self) -> str:
        # Aquí puedes agregar lógica para construir la clave secreta
        # Por ejemplo, podrías cargarla desde un archivo o generarla
        return self.SECRET_KEY
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Permite campos extra en el entorno
    }

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()