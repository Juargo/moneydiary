from fastapi import APIRouter

from app.api.v1.patterns import router as patterns_router
from app.api.v1.subcategories import router as subcategories_router
from app.api.v1.transactions import router as transactions_router

# Create the main v1 API router
api_v1_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_v1_router.include_router(patterns_router)
api_v1_router.include_router(subcategories_router)
api_v1_router.include_router(transactions_router)
