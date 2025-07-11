from fastapi import APIRouter
from .endpoints import auth, accounts
from .endpoints import banks  # Añadir esta importación
from .endpoints import transactions

api_router = APIRouter()

# Rutas para los distintos recursos
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
# api_router.include_router(banks.router, prefix="/banks", tags=["banks"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])