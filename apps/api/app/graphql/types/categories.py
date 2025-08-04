from __future__ import annotations
import strawberry
from typing import Optional, List
from datetime import datetime

from ...models.categories import CategoryGroup as CategoryGroupModel, Category as CategoryModel, Subcategory as SubcategoryModel


@strawberry.type
class Subcategory:
    id: int
    category_id: int
    name: str
    display_order: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@strawberry.type
class Category:
    id: int
    category_group_id: int
    name: str
    is_income: bool
    icon: Optional[str] = None
    display_order: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    subcategories: List[Subcategory] = strawberry.field(default_factory=list)


@strawberry.type
class CategoryGroup:
    id: int
    name: str
    is_expense: bool
    icon: Optional[str] = None
    display_order: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    categories: List[Category] = strawberry.field(default_factory=list)


def convert_subcategory_model_to_graphql(subcategory_model: SubcategoryModel) -> Subcategory:
    """Convierte un modelo SQLAlchemy Subcategory a tipo GraphQL Subcategory"""
    return Subcategory(
        id=subcategory_model.id,  # type: ignore
        category_id=subcategory_model.category_id,  # type: ignore
        name=subcategory_model.name,  # type: ignore
        display_order=subcategory_model.display_order,  # type: ignore
        created_at=subcategory_model.created_at.isoformat() if subcategory_model.created_at else None,  # type: ignore
        updated_at=subcategory_model.updated_at.isoformat() if subcategory_model.updated_at else None  # type: ignore
    )


def convert_category_model_to_graphql(category_model: CategoryModel) -> Category:
    """Convierte un modelo SQLAlchemy Category a tipo GraphQL Category"""
    subcategories = [
        convert_subcategory_model_to_graphql(sub) for sub in category_model.subcategories
    ]
    
    return Category(
        id=category_model.id,  # type: ignore
        category_group_id=category_model.category_group_id,  # type: ignore
        name=category_model.name,  # type: ignore
        is_income=category_model.is_income,  # type: ignore
        icon=category_model.icon,  # type: ignore
        display_order=category_model.display_order,  # type: ignore
        created_at=category_model.created_at.isoformat() if category_model.created_at else None,  # type: ignore
        updated_at=category_model.updated_at.isoformat() if category_model.updated_at else None,  # type: ignore
        subcategories=subcategories
    )


def convert_category_group_model_to_graphql(group_model: CategoryGroupModel) -> CategoryGroup:
    """Convierte un modelo SQLAlchemy CategoryGroup a tipo GraphQL CategoryGroup"""
    categories = [
        convert_category_model_to_graphql(cat) for cat in group_model.categories
    ]
    
    return CategoryGroup(
        id=group_model.id,  # type: ignore
        name=group_model.name,  # type: ignore
        is_expense=group_model.is_expense,  # type: ignore
        icon=group_model.icon,  # type: ignore
        display_order=group_model.display_order,  # type: ignore
        created_at=group_model.created_at.isoformat() if group_model.created_at else None,  # type: ignore
        updated_at=group_model.updated_at.isoformat() if group_model.updated_at else None,  # type: ignore
        categories=categories
    )
