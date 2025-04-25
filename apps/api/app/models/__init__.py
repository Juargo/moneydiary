"""
Módulo de modelos para la aplicación MoneyDiary.

Este módulo expone todos los modelos de la aplicación a través de un único punto de entrada,
permitiendo imports más limpios como `from app.models import User, Account`.
"""

# Base model
from .base import Base

# Usuarios
from .users import User

# Cuentas y tipos
from .account_types import AccountType
from .accounts import Account

# Categorías
from .categories import CategoryGroup, Category, Subcategory

# Métodos financieros
from .financial_methods import (
    FinancialMethod, MethodFiftyThirtyTwenty, MethodEnvelope,
    MethodZeroBased, MethodKakebo, MethodPayYourselfFirst
)

# Presupuestos y sobres
from .envelopes import Envelope
from .budget import BudgetPlan, BudgetItem

# Transacciones y patrones
from .transactions import TransactionStatus, Transaction
from .recurring_patterns import RecurringPattern

# Metas financieras
from .financial_goals import FinancialGoal, GoalContribution

# Proyecciones y simulaciones
from .projections import ProjectionSettings, MonthlyProjections, ProjectionDetails
from .simulations import (
    FinancialSimulation, SimulationScenario,
    SimulationParameter, SimulationResult
)

# Importación de CSV
from .csv_imports import CsvImport, CsvImportProfile, CsvColumnMapping, ImportError

# Lista de todos los modelos para facilitar imports
__all__ = [
    # Base
    'Base',
    
    # Usuarios
    'User',
    
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