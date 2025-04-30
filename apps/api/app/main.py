# FastAPI
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# Imports internos
from .lifecycle import lifespan, VERSION
from .routers import basic, auth
from .init_db import initialize_database
from .middleware import setup_middleware
from .middleware import setup_middleware
from .graphql.schema import schema
from .graphql.context import get_context
from .api.router import api_router

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
app.include_router(auth.router)

# GraphQL endpoint
graphql_router = GraphQLRouter(
    schema=schema,
    context_getter=get_context,
    graphiql=True  # Activar GraphiQL para desarrollo
)
app.include_router(graphql_router, prefix="/graphql")
app.include_router(api_router, prefix="/api/v1", tags=["api"])