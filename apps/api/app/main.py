# FastAPI
from fastapi import FastAPI

# Imports internos
from .lifecycle import lifespan, VERSION
from .routers import basic
from .init_db import initialize_database
from .middleware import setup_middleware

# Crear app
app = FastAPI(
    title="MoneyDiary API",
    description="API for the MoneyDiary app",
    version=VERSION,
    lifespan=lifespan
)

# Initialize database
initialize_database()

# Configure middleware
setup_middleware(app)

# Include routers
app.include_router(basic.router)

# Additional routers can be included as they are implemented
# app.include_router(api_router, prefix="/api")
