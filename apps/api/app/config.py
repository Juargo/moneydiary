import os
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from functools import lru_cache

class Settings(BaseSettings):
    # Ambiente
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_PORT: int = 8000
    SECRET_KEY: str = "desarrollo-inseguro-key"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "moneydiary"
    DB_USER: str = "moneydiary"
    DB_PASSWORD: str = "moneydiary_password"
    DATABASE_URL: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Construir DATABASE_URL si no está definido explícitamente
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
