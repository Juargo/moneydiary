from __future__ import annotations
import strawberry
from typing import List, Optional, TYPE_CHECKING

from ..types.bank import Bank, convert_bank_model_to_graphql
from ...services.bank_service import get_all_banks

if TYPE_CHECKING:
    from strawberry.types import Info

@strawberry.field
def get_banks(info: "Info", active_only: bool = True) -> List[Bank]:
    """Obtiene todos los bancos del sistema"""
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener los bancos (SQLAlchemy models)
    bank_models = get_all_banks(db, active_only=active_only)
    
    # Convertir los modelos SQLAlchemy a tipos GraphQL
    banks = [convert_bank_model_to_graphql(model) for model in bank_models]
    
    return banks

# @strawberry.field
# def get_bank(info: "Info", bank_id: int) -> Optional[Bank]:
#     """Obtiene un banco por su ID"""
#     # Obtener la sesión de base de datos del contexto
#     db = info.context.db
    
#     # Obtener el banco (SQLAlchemy model)
#     bank_model = get_bank_by_id(db, bank_id)
    
#     if not bank_model:
#         return None
    
#     # Convertir el modelo SQLAlchemy a tipo GraphQL
#     return convert_bank_model_to_graphql(bank_model)

# @strawberry.field
# def get_bank_by_code_query(info: "Info", bank_code: str) -> Optional[Bank]:
#     """Obtiene un banco por su código"""
#     # Obtener la sesión de base de datos del contexto
#     db = info.context.db
    
#     # Obtener el banco (SQLAlchemy model)
#     bank_model = get_bank_by_code(db, bank_code)
    
#     if not bank_model:
#         return None
    
#     # Convertir el modelo SQLAlchemy a tipo GraphQL
#     return convert_bank_model_to_graphql(bank_model)