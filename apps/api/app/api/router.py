from fastapi import APIRouter
from .endpoints import auth
from .endpoints import banks  # Añadir esta importación

api_router = APIRouter()

# Rutas para los distintos recursos
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(banks.router, prefix="/banks", tags=["banks"])  # Añadir esta línea