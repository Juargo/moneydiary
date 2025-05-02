"""
Módulo de modelos para la aplicación MoneyDiary.

Este módulo expone todos los modelos de la aplicación a través de un único punto de entrada,
permitiendo imports más limpios como `from apps.api.app.models import User, Account`.
"""

# Base model
from .base import Base

# Usuarios y autenticación - primero
from .permission import Permission
from .role import Role
from .users import User
from .oauth2_token import OAuth2Token
from .invalidated_token import InvalidatedToken

# Categorías - segundo
from .categories import CategoryGroup, Category, Subcategory

# Cuentas y tipos
from .account_types import AccountType
from .accounts import Account

# Métodos financieros
from .financial_methods import (
    FinancialMethod, MethodFiftyThirtyTwenty, MethodEnvelope,
    MethodZeroBased, MethodKakebo, MethodPayYourselfFirst
)
from .user_financial_methods import user_financial_methods

# Importación de CSV
from .csv_imports import CsvImport, CsvImportProfile, CsvColumnMapping, ImportError

# Presupuestos y sobres
from .envelopes import Envelope
from .budget import BudgetPlan, BudgetItem

# Metas financieras
from .financial_goals import FinancialGoal, GoalContribution

# Patrones recurrentes
from .recurring_patterns import RecurringPattern

# Transacciones - último ya que depende de muchos modelos anteriores
from .transactions import TransactionStatus, Transaction

# Proyecciones y simulaciones
from .projections import ProjectionSettings, MonthlyProjections, ProjectionDetails
from .simulations import (
    FinancialSimulation, SimulationScenario,
    SimulationParameter, SimulationResult
)

# Lista de todos los modelos para facilitar imports
__all__ = [
    # Base
    'Base',
    
    # Usuarios y autenticación
    'User', 'Role', 'Permission', 'OAuth2Token', 'InvalidatedToken',
    
    # Cuentas
    'AccountType', 'Account',
    
    # Categorías
    'CategoryGroup', 'Category', 'Subcategory',
    
    # Métodos financieros
    'FinancialMethod', 'MethodFiftyThirtyTwenty', 'MethodEnvelope',
    'MethodZeroBased', 'MethodKakebo', 'MethodPayYourselfFirst',
    
    # Presupuestos
    'Envelope', 'BudgetPlan', 'BudgetItem',
    
    # Transacciones
    'TransactionStatus', 'Transaction', 'RecurringPattern',
    
    # Metas
    'FinancialGoal', 'GoalContribution',
    
    # Proyecciones
    'ProjectionSettings', 'MonthlyProjections', 'ProjectionDetails',
    
    # Simulaciones
    'FinancialSimulation', 'SimulationScenario',
    'SimulationParameter', 'SimulationResult',
    
    # CSV
    'CsvImport', 'CsvImportProfile', 'CsvColumnMapping', 'ImportError'
]