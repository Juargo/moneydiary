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
    # Import models in correct dependency order
    print("Importing models...")
    import logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.orm').setLevel(logging.DEBUG)
    from apps.api.app.models.base import Base
    from apps.api.app.models.permission import Permission
    from apps.api.app.models.role import Role
    from apps.api.app.models.users import User
    from apps.api.app.models.oauth2_token import OAuth2Token
    from apps.api.app.models.invalidated_token import InvalidatedToken
    from apps.api.app.models.categories import CategoryGroup, Category, Subcategory
    from apps.api.app.models.account_types import AccountType
    from apps.api.app.models.accounts import Account
    from apps.api.app.models.financial_methods import (
        FinancialMethod, MethodFiftyThirtyTwenty, MethodEnvelope,
        MethodZeroBased, MethodKakebo, MethodPayYourselfFirst
    )
    from apps.api.app.models.user_financial_methods import user_financial_methods
    from apps.api.app.models.csv_imports import CsvImport, CsvImportProfile, CsvColumnMapping, ImportError
    from apps.api.app.models.envelopes import Envelope
    from apps.api.app.models.budget import BudgetPlan, BudgetItem
    from apps.api.app.models.financial_goals import FinancialGoal, GoalContribution
    from apps.api.app.models.recurring_patterns import RecurringPattern
    from apps.api.app.models.transactions import TransactionStatus, Transaction
    from apps.api.app.models.projections import ProjectionSettings, MonthlyProjections, ProjectionDetails
    from apps.api.app.models.simulations import (
        FinancialSimulation, SimulationScenario,
        SimulationParameter, SimulationResult
    )
    
    # Configure mappers after all models are imported
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