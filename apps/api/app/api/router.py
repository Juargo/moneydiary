from fastapi import APIRouter
from .endpoints import accounts, transactions, users, auth

api_router = APIRouter()

# Rutas para los distintos recursos
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])