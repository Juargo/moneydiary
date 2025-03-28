""" Main module for the FastAPI application. """

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from tortoise.contrib.fastapi import register_tortoise

from app.graphql.schema import schema
from app.db.config import TORTOISE_ORM


app = FastAPI()

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
    return {"message": "Money Diary API is running"}
