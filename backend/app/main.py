"""Main module for the FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from tortoise.contrib.fastapi import register_tortoise

from app.graphql.schema import schema
from app.db.config import TORTOISE_ORM


app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Permitir todos los orígenes, en producción especifica los dominios exactos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todas las cabeceras
)

# Registro de Tortoise ORM con FastAPI
# Cambiamos generate_schemas a False para evitar el warning
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,  # Cambio aquí para evitar la advertencia
    add_exception_handlers=True,
)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """Root endpoint for the FastAPI application."""
    return {"message": "Money Diary API is running"}
