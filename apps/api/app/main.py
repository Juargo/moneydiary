"""
MoneyDiary API Main Module

Este módulo es el punto de entrada principal de la API de MoneyDiary.
Coordina la inicialización de la aplicación, la configuración de servicios,
y el registro de rutas y middleware.

Arquitectura:
- Inicialización modular y desacoplada mediante funciones específicas
- Configuración de logging centralizada
- Registro de rutas API REST y GraphQL
- Configuración de middleware para procesamiento de solicitudes

Principios SOLID aplicados:
- Single Responsibility: Funciones con propósito único y bien definido
- Dependency Inversion: Uso de inyección de dependencias
- Open/Closed: Extensible mediante routers y middleware

Patrón de aplicación:
- Factory para la creación de la aplicación FastAPI
- Builder para la configuración progresiva de componentes
"""

# FastAPI
from fastapi import FastAPI

# FastAPI GraphQL
from strawberry.fastapi import GraphQLRouter

# SQLAlchemy
from sqlalchemy.orm import configure_mappers

# logging
import logging
from typing import Callable, Dict, Any

# Imports internos
from .lifecycle import lifespan, VERSION
from .middleware import setup_middleware

# Router imports
from .routers import basic
from .api.router import api_router

# Database imports
from .init_db import initialize_database

# GraphQL imports
from .graphql.schema import schema
from .graphql.context import get_context
from .graphql.client_utils import SnakeCaseGraphQLMiddleware
from .graphql.debug import debug_query, debug_result

from .services.bank_service import BankService
from .services.auth_service import AuthService
from .services.user_service import UserService

# Configuración de logging mejorada con formato
def configure_logging():
    """
    Configura el sistema de logging con un formato detallado
    para facilitar el diagnóstico de problemas.
    
    El logger 'moneydiary.api' es el logger principal de la aplicación.
    """
    logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logging_format)
    logger = logging.getLogger("moneydiary.api")
    logger.setLevel(logging.DEBUG)
    return logger

# Logger centralizado
logger = configure_logging()

def import_models():
    """
    Importa los modelos de la aplicación en el orden correcto para evitar
    dependencias circulares y garantizar una inicialización adecuada.
    
    Organiza los modelos por dominios funcionales para mejorar la legibilidad
    y mantenibilidad.
    """
    logger.debug("Importando modelos de la base de datos...")
    
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
    
    logger.debug("Modelos importados correctamente")

def setup_database():
    """
    Configura e inicializa la base de datos.
    - Configura los mappers de SQLAlchemy
    - Inicializa las tablas y datos iniciales si es necesario
    """
    logger.debug("Configurando mappers de SQLAlchemy...")
    configure_mappers()
    
    logger.debug("Inicializando base de datos...")
    initialize_database()
    
    logger.debug("Inicialización de base de datos completada")

def initialize_app():
    """
    Inicializa la aplicación importando modelos en orden correcto,
    configurando mappers SQLAlchemy e inicializando la base de datos.
    
    Sigue el principio de responsabilidad única separando las tareas
    en funciones especializadas.
    """
    import_models()
    setup_database()

def create_graphql_router() -> GraphQLRouter:
    """
    Crea y configura el router GraphQL con la configuración adecuada.
    
    Returns:
        GraphQLRouter: Router configurado para manejar consultas GraphQL
    """
    logger.debug("Configurando router GraphQL...")
    return GraphQLRouter(
        schema=schema,
        context_getter=get_context,
        graphiql=True,  # Activar GraphiQL para desarrollo
        debug=True
    )

def create_application() -> FastAPI:
    """
    Factory function que crea y configura la aplicación FastAPI.
    Sigue el patrón Factory para desacoplar la creación del objeto
    de su uso.
    
    Returns:
        FastAPI: Aplicación FastAPI completamente configurada
    """
    # Crear la aplicación con los metadatos apropiados
    app = FastAPI(
        title="MoneyDiary API",
        description="API para la aplicación MoneyDiary - Gestión financiera personal",
        version=VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Inicializar la base de datos
    initialize_app()
    
    # Configurar middleware
    setup_middleware(app)
    
    # Middleware para conversión snake_case/camelCase en GraphQL
    app.add_middleware(SnakeCaseGraphQLMiddleware)
    
    # Registrar routers
    app.include_router(basic.router)
    app.include_router(create_graphql_router(), prefix="/graphql")
    app.include_router(api_router, prefix="/api/v1", tags=["api"])
    
    logger.info("MoneyDiary API inicializada correctamente")
    return app

# Crear la instancia de la aplicación utilizando el factory
app = create_application()

# Esta línea es útil para depuración y para confirmación de inicialización correcta
logger.debug("MoneyDiary API inicializada con GraphQL y debugging habilitados")