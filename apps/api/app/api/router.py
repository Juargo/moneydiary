from fastapi import APIRouter
from .endpoints import auth

api_router = APIRouter()

# Rutas para los distintos recursos
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])