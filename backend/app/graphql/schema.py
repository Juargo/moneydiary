""" Esquema de GraphQL """
from typing import List, Optional

import strawberry
from app.db.models.user import User as UserModel
from app.db.models.budget import Budget as BudgetModel
from app.db.models.category import Category as CategoryModel
from app.db.models.subcategory import Subcategory as SubcategoryModel
from app.db.models.pattern import Pattern as PatternModel


@strawberry.type
class User:
    """ Tipo GraphQL para usuarios """
    id: int
    username: str
    # Cambiando los nombres de los campos para seguir la convención de camelCase de GraphQL
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class Budget:
    """ Tipo GraphQL para presupuestos """
    id: int
    user: int = strawberry.field(name="user")
    name: str
    description: Optional[str] = strawberry.field(name="description")
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class Category:
    """ Tipo GraphQL para categorías """
    id: int
    budget_id: int = strawberry.field(name="budgetId")
    name: str
    description: Optional[str]
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class Subcategory:
    """ Tipo GraphQL para subcategorías """
    id: int
    category_id: int = strawberry.field(name="categoryId")
    name: str
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class Pattern:
    """ Tipo GraphQL para patrones de transacciones """
    id: int
    user_id: int = strawberry.field(name="userId")
    pattern: str
    category_id: int = strawberry.field(name="categoryId")
    subcategory_id: Optional[int] = strawberry.field(name="subcategoryId")
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class Query:

    @strawberry.field
    async def user(self, user_id: int) -> Optional[User]:
        """ Obtener usuario por ID """
        user = await UserModel.get_or_none(id=user_id)
        if user:
            return User(
                id=user.id,
                username=user.username,
                created_at=str(user.created_at),
                updated_at=str(user.updated_at)
            )
        return None

    @strawberry.field
    async def users(self) -> List[User]:
        """ Obtener todos los usuarios """
        users = await UserModel.all()
        return [
            User(
                id=user.id,
                username=user.username,
                created_at=str(user.created_at),
                updated_at=str(user.updated_at)
            )
            for user in users
        ]

    @strawberry.field
    async def budgets(self, user_id: int) -> List[Budget]:
        """ Obtener todos los presupuestos de un usuario """
        budgets = await BudgetModel.filter(user=user_id)
        return [
            Budget(
                id=budget.id,
                user=budget.user_id,
                name=budget.name,
                description=budget.description,
                created_at=str(budget.created_at),
                updated_at=str(budget.updated_at)
            )
            for budget in budgets
        ]

    @strawberry.field
    async def categories(self, budget_id: int) -> List[Category]:
        """ Obtener todas las categorías de un presupuesto """
        categories = await CategoryModel.filter(budget_id=budget_id)
        return [
            Category(
                id=category.id,
                budget_id=category.budget_id,
                name=category.name,
                description=category.description,
                created_at=str(category.created_at),
                updated_at=str(category.updated_at)
            )
            for category in categories
        ]

    @strawberry.field
    async def subcategories(self, category_id: int) -> List[Subcategory]:
        """ Obtener todas las subcategorías de una categoría """
        subcategories = await SubcategoryModel.filter(category_id=category_id)
        return [
            Subcategory(
                id=subcategory.id,
                category_id=subcategory.category_id,
                name=subcategory.name,
                created_at=str(subcategory.created_at),
                updated_at=str(subcategory.updated_at)
            )
            for subcategory in subcategories
        ]

    @strawberry.field
    async def patterns(self, user_id: int) -> List[Pattern]:
        """ Obtener todos los patrones de un usuario """
        patterns = await PatternModel.filter(user_id=user_id)
        return [
            Pattern(
                id=pattern.id,
                user_id=pattern.user_id,
                pattern=pattern.pattern,
                category_id=pattern.category_id,
                subcategory_id=pattern.subcategory_id,
                created_at=str(pattern.created_at),
                updated_at=str(pattern.updated_at)
            )
            for pattern in patterns
        ]

schema = strawberry.Schema(query=Query)
