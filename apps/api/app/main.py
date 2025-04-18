from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
from .version import __version__

# Esquema GraphQL de ejemplo
@strawberry.type
class Query:
    @strawberry.field
    def hello() -> str:
        return "Hello, MoneyDiary!"

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

# Crear aplicación FastAPI
app = FastAPI(
    title="MoneyDiary API",
    description="API para la gestión de finanzas personales",
    version=__version__
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir ruta GraphQL
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "app": "MoneyDiary API", 
        "version": __version__,
        "graphql_endpoint": "/graphql"
        }