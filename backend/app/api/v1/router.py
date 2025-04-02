from fastapi import APIRouter

from app.api.v1.patterns import router as patterns_router

# Create the main v1 API router
api_v1_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_v1_router.include_router(patterns_router)
