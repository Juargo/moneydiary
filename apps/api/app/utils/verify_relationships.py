from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.properties import RelationshipProperty
import inspect
from typing import Set, Dict, List, Tuple
import sys
import os

# Asegurarse de que el directorio raíz esté en el path de Python
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

# Importar todos los modelos a nivel de módulo
from apps.api.app.models.base import Base
# Importaciones explícitas de los modelos
from apps.api.app.models.users import User
from apps.api.app.models.accounts import Account
from apps.api.app.models.categories import Category, CategoryGroup, Subcategory
from apps.api.app.models.transactions import Transaction, TransactionStatus
from apps.api.app.models.financial_methods import (
    FinancialMethod, MethodFiftyThirtyTwenty, MethodEnvelope,
    MethodZeroBased, MethodKakebo, MethodPayYourselfFirst
)
from apps.api.app.models.envelopes import Envelope
from apps.api.app.models.budget import BudgetPlan, BudgetItem
from apps.api.app.models.file_imports import CsvImport, CsvImportProfile, CsvColumnMapping
from apps.api.app.models.financial_goals import FinancialGoal, GoalContribution
from apps.api.app.models.projections import ProjectionSettings, MonthlyProjections, ProjectionDetails
from apps.api.app.models.simulations import (
    FinancialSimulation, SimulationScenario, 
    SimulationParameter, SimulationResult
)
from apps.api.app.models.oauth2_token import OAuth2Token
from apps.api.app.models.invalidated_token import InvalidatedToken
from apps.api.app.models.recurring_patterns import RecurringPattern
from apps.api.app.models.role import Role
from apps.api.app.models.permission import Permission
from apps.api.app.models.account_types import AccountType

def get_all_models():
    """Importa y retorna todos los modelos declarativos SQLAlchemy"""
    # Método alternativo para encontrar todos los modelos
    models = []
    
    # Opción 1: Usar las clases importadas directamente
    imported_classes = [User, Account, Category, CategoryGroup, Subcategory, Transaction, 
                        TransactionStatus, FinancialMethod, MethodFiftyThirtyTwenty, MethodEnvelope,
                        MethodZeroBased, MethodKakebo, MethodPayYourselfFirst, Envelope,
                        BudgetPlan, BudgetItem, CsvImport, CsvImportProfile, CsvColumnMapping,
                        FinancialGoal, GoalContribution, ProjectionSettings, MonthlyProjections, 
                        ProjectionDetails, FinancialSimulation, SimulationScenario, 
                        SimulationParameter, SimulationResult, OAuth2Token, InvalidatedToken,
                        RecurringPattern, Role, Permission, AccountType]
    
    for cls in imported_classes:
        if hasattr(cls, "__tablename__"):
            models.append(cls)
    
    # Opción alternativa si Base.metadata está disponible
    # Este método es más robusto porque encontrará todas las clases
    # registradas en la metadata de Base
    try:
        for table in Base.metadata.tables.values():
            for mapper in _get_all_mappers():
                if mapper.local_table == table:
                    models.append(mapper.class_)
                    break
    except Exception as e:
        print(f"Advertencia: No se pudo usar metadata para encontrar modelos: {str(e)}")
        print("Usando solo las clases importadas explícitamente.")
    
    # Eliminar duplicados
    unique_models = []
    model_names = set()
    for model in models:
        if model.__name__ not in model_names:
            unique_models.append(model)
            model_names.add(model.__name__)
    
    return unique_models

def _get_all_mappers():
    """Obtiene todos los mappers registrados en SQLAlchemy"""
    from sqlalchemy.orm import _mapper_registry
    return _mapper_registry.mappers

def verify_relationships():
    """Verifica todas las relaciones bidireccionales en los modelos"""
    models = get_all_models()
    print(f"Verificando {len(models)} modelos...")
    
    relationship_errors = []
    
    for model in models:
        model_name = model.__name__
        print(f"\nVerificando modelo: {model_name}")
        
        try:
            mapper = class_mapper(model)
            
            for prop in mapper.iterate_properties:
                if isinstance(prop, RelationshipProperty):
                    relationship_name = prop.key
                    target_model = prop.mapper.class_.__name__
                    
                    print(f"  Relación: {relationship_name} -> {target_model}", end="")
                    
                    if prop.back_populates:
                        print(f" (back_populates='{prop.back_populates}')")
                        
                        # Verificar si la relación inversa existe
                        try:
                            back_mapper = class_mapper(prop.mapper.class_)
                            back_mapper.get_property(prop.back_populates)
                            print(f"    ✓ Relación inversa encontrada")
                        except Exception as e:
                            error_msg = f"    ✗ ERROR: {str(e)}"
                            print(error_msg)
                            relationship_errors.append({
                                'model': model_name,
                                'relation': relationship_name,
                                'target': target_model,
                                'expected_back': prop.back_populates,
                                'error': str(e)
                            })
                    else:
                        print(f" (sin back_populates)")
        except Exception as e:
            print(f"  ✗ ERROR al mapear modelo {model_name}: {str(e)}")
    
    # Resumen de errores
    if relationship_errors:
        print("\n\n===== RESUMEN DE ERRORES =====")
        print(f"Se encontraron {len(relationship_errors)} errores en relaciones:")
        
        for i, error in enumerate(relationship_errors, 1):
            print(f"\n{i}. Problema en {error['model']}.{error['relation']} -> {error['target']}")
            print(f"   Espera que {error['target']} tenga una propiedad '{error['expected_back']}'")
            print(f"   Error: {error['error']}")
            
        print("\n=== SUGERENCIAS DE CORRECCIÓN ===")
        
        for error in relationship_errors:
            print(f"\n• Para corregir {error['model']}.{error['relation']} -> {error['target']}:")
            print(f"  Opción 1: Agregar en {error['target']}:")
            print(f"    {error['expected_back']} = relationship(\"{error['model']}\", back_populates=\"{error['relation']}\")")
            print(f"  Opción 2: Modificar en {error['model']}:")
            print(f"    {error['relation']} = relationship(\"{error['target']}\")  # Sin back_populates")
    else:
        print("\n✅ ¡No se encontraron errores en las relaciones!")
    
    return relationship_errors

if __name__ == "__main__":
    print("Verificando relaciones SQLAlchemy...")
    errors = verify_relationships()
    
    sys.exit(1 if errors else 0)