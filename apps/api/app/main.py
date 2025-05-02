# FastAPI
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import configure_mappers

# Imports internos
from .lifecycle import lifespan, VERSION
from .routers import basic
from .api.endpoints import auth
from .init_db import initialize_database
from .middleware import setup_middleware
from .middleware import setup_middleware
from .graphql.schema import schema
from .graphql.context import get_context
from .api.router import api_router

# Función para inicializar la aplicación y configurar mappers
def initialize_app():
    # Importar todos los modelos para asegurar que SQLAlchemy los vea
    import apps.api.app.models
    
    # Forzar la configuración de mappers antes de usar la BD
    print("Configurando mappers de SQLAlchemy...")
    configure_mappers()
    
    # Inicializar base de datos
    print("Inicializando base de datos...")
    initialize_database()
    
    print("Inicialización completada")

# Crear app
app = FastAPI(
    title="MoneyDiary API",
    description="API for the MoneyDiary app",
    version=VERSION,
    lifespan=lifespan
)

# Initialize database
initialize_app()

# Configure middleware
setup_middleware(app)

# Include routers
app.include_router(basic.router)
# app.include_router(auth.router)

# GraphQL endpoint
graphql_router = GraphQLRouter(
    schema=schema,
    context_getter=get_context,
    graphiql=True  # Activar GraphiQL para desarrollo
)
app.include_router(graphql_router, prefix="/graphql")
app.include_router(api_router, prefix="/api/v1", tags=["api"])