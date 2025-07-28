from fastapi import APIRouter

from .endpoints import auth, accounts
from .endpoints import banks  # Añadir esta importación
from .endpoints import transactions
from .endpoints import import_profiles
from ..routers import description_patterns

api_router = APIRouter()

# Rutas para los distintos recursos
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
# api_router.include_router(banks.router, prefix="/banks", tags=["banks"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(import_profiles.router, prefix="/import-profiles", tags=["import-profiles"])
api_router.include_router(description_patterns.router, tags=["description-patterns"])
