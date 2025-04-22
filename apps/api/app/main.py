from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session
from sqlalchemy import text

from .version import __version__
from .config import settings
from .database import engine, Base, get_db, DB_HOST, DB_PORT, DB_NAME, DB_USER
from .graphql.schema import schema as graphql_schema
# from .api import api_router

# Crear tablas en la BD al iniciar (en desarrollo, para producción usar Alembic)
# if settings.ENVIRONMENT != "production":
#     Base.metadata.create_all(bind=engine)

# Configuración de la aplicación FastAPI
app = FastAPI(
    title="MoneyDiary API",
    description="API para el sistema MoneyDiary de finanzas personales",
    version=__version__,
    debug=settings.DEBUG
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración GraphQL
graphql_router = GraphQLRouter(graphql_schema)

# Incluir rutas
app.include_router(graphql_router, prefix="/graphql")
# app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": f"MoneyDiary API v{__version__}",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "graphql_endpoint": "/graphql",
        "api_endpoint": "/api"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # Verifica la conexión a la base de datos
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        # Mostrar la URL de conexión (ocultando la contraseña) para diagnóstico
        connection_url = str(engine.url)
        # Ocultar la contraseña para seguridad
        if '@' in connection_url:
            masked_url = connection_url.split('@')
            auth_part = masked_url[0].split(':')
            if len(auth_part) > 2:
                auth_part[2] = '****'  # Oculta la contraseña
                masked_url[0] = ':'.join(auth_part)
            connection_url = '@'.join(masked_url)
        
        db_status = {
            "error": str(e),
            "connection_url": connection_url,
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME,
            "user": DB_USER
        }
    
    return {
        "status": "ok" if db_status == "ok" else "error",
        "version": __version__,
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }