# FastAPI
from fastapi import FastAPI

# FastAPI GraphQL
from strawberry.fastapi import GraphQLRouter

# SQLAlchemy
from sqlalchemy.orm import configure_mappers

# logging
import logging

# Imports internos
from .lifecycle import lifespan, VERSION
from .middleware import setup_middleware

# Router imports
from .routers import basic
from .api.endpoints import auth
from .api.router import api_router

# Database imports
from .init_db import initialize_database

# GraphQL imports
from .graphql.schema import schema
from .graphql.context import get_context
from .graphql.client_utils import SnakeCaseGraphQLMiddleware
from .graphql.debug import debug_query, debug_result

from .services.bank_service import BankService 

# Configure more detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("moneydiary.api")
logger.setLevel(logging.DEBUG)

# Función para inicializar la aplicación y configurar mappers
def initialize_app():
    """
    Inicializa la aplicación importando modelos en orden correcto,
    configurando mappers SQLAlchemy e inicializando la base de datos.
    """
    # Agrupar importaciones por dominio funcional
    # Base y autenticación
    from apps.api.app.models.base import Base
    from apps.api.app.models.permission import Permission
    from apps.api.app.models.role import Role
    from apps.api.app.models.users import User
    from apps.api.app.models.oauth2_token import OAuth2Token
    from apps.api.app.models.invalidated_token import InvalidatedToken
    
    # Categorías y cuentas
    from apps.api.app.models.categories import CategoryGroup, Category, Subcategory
    from apps.api.app.models.account_types import AccountType
    from apps.api.app.models.accounts import Account
    
    # Métodos financieros
    from apps.api.app.models.financial_methods import (
        FinancialMethod, MethodFiftyThirtyTwenty, MethodEnvelope,
        MethodZeroBased, MethodKakebo, MethodPayYourselfFirst
    )
    from apps.api.app.models.user_financial_methods import user_financial_methods
    from apps.api.app.models.envelopes import Envelope
    
    # Presupuestos y objetivos
    from apps.api.app.models.budget import BudgetPlan, BudgetItem
    from apps.api.app.models.financial_goals import FinancialGoal, GoalContribution
    
    # Transacciones y patrones
    from apps.api.app.models.recurring_patterns import RecurringPattern
    from apps.api.app.models.transactions import TransactionStatus, Transaction
    
    # Proyecciones y simulaciones
    from apps.api.app.models.projections import ProjectionSettings, MonthlyProjections, ProjectionDetails
    from apps.api.app.models.simulations import (
        FinancialSimulation, SimulationScenario,
        SimulationParameter, SimulationResult
    )
    
    # Importación de datos
    from apps.api.app.models.csv_imports import CsvImport, CsvImportProfile, CsvColumnMapping, ImportError
    
    
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

# Add the SnakeCaseGraphQLMiddleware to handle snake_case/camelCase conversion
# Fix the middleware initialization by passing app
app.add_middleware(SnakeCaseGraphQLMiddleware)

# Include routers
app.include_router(basic.router)
# app.include_router(auth.router)

# GraphQL endpoint with proper configuration and debugging
graphql_router = GraphQLRouter(
    schema=schema,
    context_getter=get_context,
    graphiql=True,  # Activar GraphiQL para desarrollo
    debug=True
)
app.include_router(graphql_router, prefix="/graphql")
app.include_router(api_router, prefix="/api/v1", tags=["api"])

# Log application startup for debugging
logger.debug("MoneyDiary API initialized with GraphQL debugging")