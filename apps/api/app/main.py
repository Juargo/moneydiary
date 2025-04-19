from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
from .version import __version__
from .config import settings

# Placeholder para el esquema GraphQL
@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return __version__

    @strawberry.field
    def hello(self) -> str:
        return "Hello from MoneyDiary API!"

schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema)

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

# Rutas
app.include_router(graphql_router, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": f"MoneyDiary API v{__version__}",
        "environment": settings.ENVIRONMENT,
        "graphql_endpoint": "/graphql"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
