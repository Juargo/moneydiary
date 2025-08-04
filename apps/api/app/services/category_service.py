from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from typing import List, Optional, cast
from datetime import datetime

from ..models.categories import CategoryGroup, Category, Subcategory
from ..schemas.categories import (
    CategoryGroupCreateRequest, CategoryGroupUpdateRequest,
    CategoryCreateRequest, CategoryUpdateRequest,
    SubcategoryCreateRequest, SubcategoryUpdateRequest
)


# CategoryGroup services
def get_user_category_groups(db: Session, user_id: int) -> List[CategoryGroup]:
    """Obtiene todos los grupos de categorías de un usuario con sus categorías y subcategorías"""
    # Note: Assuming CategoryGroup has user_id field. If not, we'll need to adjust based on your model
    result = db.execute(
        select(CategoryGroup)
        .options(
            joinedload(CategoryGroup.categories).joinedload(Category.subcategories)
        )
        .order_by(CategoryGroup.display_order, CategoryGroup.name)
    )
    return cast(List[CategoryGroup], result.scalars().unique().all())


def get_category_group_by_id(db: Session, user_id: int, group_id: int) -> Optional[CategoryGroup]:
    """Obtiene un grupo de categorías específico por ID"""
    result = db.execute(
        select(CategoryGroup)
        .options(
            joinedload(CategoryGroup.categories).joinedload(Category.subcategories)
        )
        .where(CategoryGroup.id == group_id)
    )
    return result.scalar_one_or_none()


def create_category_group(db: Session, user_id: int, group_data: CategoryGroupCreateRequest) -> CategoryGroup:
    """Crea un nuevo grupo de categorías"""
    db_group = CategoryGroup(
        name=group_data.name,
        is_expense=group_data.is_expense,
        icon=group_data.icon,
        display_order=group_data.display_order,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    return db_group


def update_category_group(db: Session, user_id: int, group_id: int, group_data: CategoryGroupUpdateRequest) -> Optional[CategoryGroup]:
    """Actualiza un grupo de categorías existente"""
    db_group = db.execute(
        select(CategoryGroup).where(CategoryGroup.id == group_id)
    ).scalar_one_or_none()
    
    if not db_group:
        return None
    
    # Update only provided fields
    update_data = group_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_group, field, value)
    
    setattr(db_group, 'updated_at', datetime.utcnow())
    
    db.commit()
    db.refresh(db_group)
    
    return db_group


def delete_category_group(db: Session, user_id: int, group_id: int) -> bool:
    """Elimina un grupo de categorías"""
    db_group = db.execute(
        select(CategoryGroup).where(CategoryGroup.id == group_id)
    ).scalar_one_or_none()
    
    if not db_group:
        return False
    
    db.delete(db_group)
    db.commit()
    
    return True


# Category services
def get_categories_by_group(db: Session, user_id: int, group_id: int) -> List[Category]:
    """Obtiene todas las categorías de un grupo específico"""
    result = db.execute(
        select(Category)
        .options(joinedload(Category.subcategories))
        .where(Category.category_group_id == group_id)
        .order_by(Category.display_order, Category.name)
    )
    return cast(List[Category], result.scalars().unique().all())


def get_category_by_id(db: Session, user_id: int, category_id: int) -> Optional[Category]:
    """Obtiene una categoría específica por ID"""
    result = db.execute(
        select(Category)
        .options(
            joinedload(Category.subcategories),
            joinedload(Category.category_group)
        )
        .where(Category.id == category_id)
    )
    return result.scalar_one_or_none()


def create_category(db: Session, user_id: int, category_data: CategoryCreateRequest) -> Category:
    """Crea una nueva categoría"""
    db_category = Category(
        category_group_id=category_data.category_group_id,
        name=category_data.name,
        is_income=category_data.is_income,
        icon=category_data.icon,
        display_order=category_data.display_order,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


def update_category(db: Session, user_id: int, category_id: int, category_data: CategoryUpdateRequest) -> Optional[Category]:
    """Actualiza una categoría existente"""
    db_category = db.execute(
        select(Category).where(Category.id == category_id)
    ).scalar_one_or_none()
    
    if not db_category:
        return None
    
    # Update only provided fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    setattr(db_category, 'updated_at', datetime.utcnow())
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


def delete_category(db: Session, user_id: int, category_id: int) -> bool:
    """Elimina una categoría"""
    db_category = db.execute(
        select(Category).where(Category.id == category_id)
    ).scalar_one_or_none()
    
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    
    return True


# Subcategory services
def get_subcategories_by_category(db: Session, user_id: int, category_id: int) -> List[Subcategory]:
    """Obtiene todas las subcategorías de una categoría específica"""
    result = db.execute(
        select(Subcategory)
        .where(Subcategory.category_id == category_id)
        .order_by(Subcategory.display_order, Subcategory.name)
    )
    return cast(List[Subcategory], result.scalars().all())


def get_subcategory_by_id(db: Session, user_id: int, subcategory_id: int) -> Optional[Subcategory]:
    """Obtiene una subcategoría específica por ID"""
    result = db.execute(
        select(Subcategory)
        .options(joinedload(Subcategory.category))
        .where(Subcategory.id == subcategory_id)
    )
    return result.scalar_one_or_none()


def create_subcategory(db: Session, user_id: int, subcategory_data: SubcategoryCreateRequest) -> Subcategory:
    """Crea una nueva subcategoría"""
    db_subcategory = Subcategory(
        category_id=subcategory_data.category_id,
        name=subcategory_data.name,
        display_order=subcategory_data.display_order,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_subcategory)
    db.commit()
    db.refresh(db_subcategory)
    
    return db_subcategory


def update_subcategory(db: Session, user_id: int, subcategory_id: int, subcategory_data: SubcategoryUpdateRequest) -> Optional[Subcategory]:
    """Actualiza una subcategoría existente"""
    db_subcategory = db.execute(
        select(Subcategory).where(Subcategory.id == subcategory_id)
    ).scalar_one_or_none()
    
    if not db_subcategory:
        return None
    
    # Update only provided fields
    update_data = subcategory_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subcategory, field, value)
    
    setattr(db_subcategory, 'updated_at', datetime.utcnow())
    
    db.commit()
    db.refresh(db_subcategory)
    
    return db_subcategory


def delete_subcategory(db: Session, user_id: int, subcategory_id: int) -> bool:
    """Elimina una subcategoría"""
    db_subcategory = db.execute(
        select(Subcategory).where(Subcategory.id == subcategory_id)
    ).scalar_one_or_none()
    
    if not db_subcategory:
        return False
    
    db.delete(db_subcategory)
    db.commit()
    
    return True
