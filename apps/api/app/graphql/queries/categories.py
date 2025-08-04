from __future__ import annotations
import strawberry
from strawberry.types import Info
from typing import List, Optional

from ..types.categories import CategoryGroup, Category, Subcategory
from ..types.categories import convert_category_group_model_to_graphql, convert_category_model_to_graphql, convert_subcategory_model_to_graphql
from ...services.category_service import (
    get_user_category_groups, get_category_group_by_id, get_categories_by_group, 
    get_category_by_id, get_subcategories_by_category, get_subcategory_by_id
)
from ...utils.auth import get_authenticated_user


async def get_my_category_groups(info: Info) -> List[CategoryGroup]:
    """Obtiene todos los grupos de categorías del usuario autenticado"""
    # Obtener el usuario autenticado desde el token JWT
    current_user = await get_authenticated_user(info)
    
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener los grupos de categorías del usuario (SQLAlchemy models)
    group_models = get_user_category_groups(db, current_user.id)  # type: ignore
    
    # Convertir los modelos SQLAlchemy a tipos GraphQL
    groups = [convert_category_group_model_to_graphql(model) for model in group_models]
    
    return groups


async def get_my_category_group(info: Info, group_id: int) -> Optional[CategoryGroup]:
    """Obtiene un grupo de categorías específico del usuario autenticado por ID"""
    # Obtener el usuario autenticado desde el token JWT
    current_user = await get_authenticated_user(info)
    
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener el grupo de categorías específico del usuario (SQLAlchemy model)
    group_model = get_category_group_by_id(db, current_user.id, group_id)  # type: ignore
    
    if not group_model:
        return None
    
    # Convertir el modelo SQLAlchemy a tipo GraphQL
    return convert_category_group_model_to_graphql(group_model)


async def get_my_categories_by_group(info: Info, group_id: int) -> List[Category]:
    """Obtiene todas las categorías de un grupo específico del usuario autenticado"""
    # Obtener el usuario autenticado desde el token JWT
    current_user = await get_authenticated_user(info)
    
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener las categorías del grupo del usuario (SQLAlchemy models)
    category_models = get_categories_by_group(db, current_user.id, group_id)  # type: ignore
    
    # Convertir los modelos SQLAlchemy a tipos GraphQL
    categories = [convert_category_model_to_graphql(model) for model in category_models]
    
    return categories


async def get_my_category(info: Info, category_id: int) -> Optional[Category]:
    """Obtiene una categoría específica del usuario autenticado por ID"""
    # Obtener el usuario autenticado desde el token JWT
    current_user = await get_authenticated_user(info)
    
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener la categoría específica del usuario (SQLAlchemy model)
    category_model = get_category_by_id(db, current_user.id, category_id)  # type: ignore
    
    if not category_model:
        return None
    
    # Convertir el modelo SQLAlchemy a tipo GraphQL
    return convert_category_model_to_graphql(category_model)


async def get_my_subcategories_by_category(info: Info, category_id: int) -> List[Subcategory]:
    """Obtiene todas las subcategorías de una categoría específica del usuario autenticado"""
    # Obtener el usuario autenticado desde el token JWT
    current_user = await get_authenticated_user(info)
    
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener las subcategorías de la categoría del usuario (SQLAlchemy models)
    subcategory_models = get_subcategories_by_category(db, current_user.id, category_id)  # type: ignore
    
    # Convertir los modelos SQLAlchemy a tipos GraphQL
    subcategories = [convert_subcategory_model_to_graphql(model) for model in subcategory_models]
    
    return subcategories


async def get_my_subcategory(info: Info, subcategory_id: int) -> Optional[Subcategory]:
    """Obtiene una subcategoría específica del usuario autenticado por ID"""
    # Obtener el usuario autenticado desde el token JWT
    current_user = await get_authenticated_user(info)
    
    # Obtener la sesión de base de datos del contexto
    db = info.context.db
    
    # Obtener la subcategoría específica del usuario (SQLAlchemy model)
    subcategory_model = get_subcategory_by_id(db, current_user.id, subcategory_id)  # type: ignore
    
    if not subcategory_model:
        return None
    
    # Convertir el modelo SQLAlchemy a tipo GraphQL
    return convert_subcategory_model_to_graphql(subcategory_model)
