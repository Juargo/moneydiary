""" Esquema de GraphQL """
from typing import List, Optional

import strawberry
from app.db.models.user import User as UserModel
from app.db.models.budget import Budget as BudgetModel
from app.db.models.category import Category as CategoryModel
from app.db.models.subcategory import Subcategory as SubcategoryModel
from app.db.models.pattern import Pattern as PatternModel
from app.db.models.bank import Bank as BankModel
from app.db.models.user_bank import UserBank as UserBankModel
from app.db.models.pattern_ignore import PatternIgnore as PatternIgnoreModel
from app.db.models.transaction import Transaction as TransactionModel, TransactionType
from tortoise.expressions import RawSQL


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
    match_text: str = strawberry.field(name="expName")
    subcategory_id: int = strawberry.field(name="subcategoryId")
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class Bank:
    """ Tipo GraphQL para bancos """
    id: int
    name: str
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class UserBank:
    """ Tipo GraphQL para la relación entre usuarios y bancos """
    id: int
    user_id: int = strawberry.field(name="userId")
    bank_id: int = strawberry.field(name="bankId")
    balance: float
    description: Optional[str]
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class PatternIgnore:
    """ Tipo GraphQL para patrones a ignorar en transacciones """
    id: int
    match_text: str = strawberry.field(name="expName")
    description: str
    user_id: int = strawberry.field(name="userId")
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")

@strawberry.type
class TransactionData:
    """ Tipo GraphQL para transacciones con datos relacionados """
    id: int
    transaction_date: str = strawberry.field(name="transactionDate")
    description: str
    amount: float
    type: str
    user_bank_id: int = strawberry.field(name="userBankId")
    subcategory_id: int = strawberry.field(name="subcategoryId")
    created_at: str = strawberry.field(name="createdAt")
    updated_at: str = strawberry.field(name="updatedAt")
    
    # Datos relacionados
    user_bank_name: str = strawberry.field(name="userBankName")
    bank_name: str = strawberry.field(name="bankName")
    subcategory_name: str = strawberry.field(name="subcategoryName")
    category_name: str = strawberry.field(name="categoryName")

@strawberry.type
class BudgetConfigData:
    """ Tipo GraphQL para la vista de configuración de presupuesto """
    user_id: int
    user_name: str
    budget_id: int
    budget_name: str
    category_id: int
    category_name: str
    subcategory_id: int
    subcategory_name: str
    subcategory_budget_amount: Optional[float]
    pattern_id: Optional[int]
    pattern_text: Optional[str]

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
    async def patterns(self, subcategory_id: int) -> List[Pattern]:
        """ Obtener todos los patrones de una subcategoría """
        patterns = await PatternModel.filter(subcategory_id=subcategory_id)
        return [
            Pattern(
                id=pattern.id,
                match_text=pattern.match_text,
                subcategory_id=pattern.subcategory_id,
                created_at=str(pattern.created_at),
                updated_at=str(pattern.updated_at)
            )
            for pattern in patterns
        ]
        
    @strawberry.field
    async def banks(self) -> List[Bank]:
        """ Obtener todos los bancos """
        banks = await BankModel.all()
        return [
            Bank(
                id=bank.id,
                name=bank.name,
                created_at=str(bank.created_at),
                updated_at=str(bank.updated_at)
            )
            for bank in banks
        ]
    
    @strawberry.field(name="userBanks")  # Explicitly name the field in camelCase for GraphQL
    async def user_banks(self, userId: int) -> List[UserBank]:
        """ Obtener todos los bancos de un usuario """
        user_banks = await UserBankModel.filter(user_id=userId).prefetch_related('bank')
        return [
            UserBank(
                id=user_bank.id,
                user_id=user_bank.user_id,
                bank_id=user_bank.bank_id,
                balance=float(user_bank.balance),
                description=user_bank.description,
                created_at=str(user_bank.created_at),
                updated_at=str(user_bank.updated_at)
            )
            for user_bank in user_banks
        ]
    
    @strawberry.field(name="patternIgnores")
    async def pattern_ignores(self, userId: int) -> List[PatternIgnore]:
        """ Obtener todos los patrones a ignorar de un usuario """
        pattern_ignores = await PatternIgnoreModel.filter(user_id=userId)
        return [
            PatternIgnore(
                id=pattern_ignore.id,
                match_text=pattern_ignore.match_text,
                description=pattern_ignore.description,
                user_id=pattern_ignore.user_id,
                created_at=str(pattern_ignore.created_at),
                updated_at=str(pattern_ignore.updated_at)
            )
            for pattern_ignore in pattern_ignores
        ]
    
    @strawberry.field(name="budgetConfig")
    async def budget_config(
        self,
        userId: int,
        budgetId: Optional[int] = None
    ) -> List[BudgetConfigData]:
        """ 
        Obtener la configuración de presupuesto desde la vista view_budget_config
        
        Args:
            userId: ID del usuario
            budgetId: ID opcional del presupuesto para filtrar
        """
        from tortoise import connections
        
        # Get the current connection
        connection = connections.get("default")
        
        # Construir la consulta SQL para la vista usando placeholders compatibles con el dialect
        if connection.capabilities.dialect == "mysql":
            # MySQL uses %s for placeholders
            query = "SELECT * FROM view_budget_config WHERE user_id = %s"
            if budgetId is not None:
                query += " AND budget_id = %s"
        else:
            # PostgreSQL and others use $1, $2, etc.
            query = "SELECT * FROM view_budget_config WHERE user_id = $1"
            if budgetId is not None:
                query += " AND budget_id = $2"
                
        # Preparar los parámetros
        params = [userId]
        if budgetId is not None:
            params.append(budgetId)
        
        # Ejecutar la consulta raw usando la conexión de Tortoise ORM
        try:
            results = await connection.execute_query(query, params)
            
            # Convertir los resultados al tipo GraphQL
            return [
                BudgetConfigData(
                    user_id=row["user_id"],
                    user_name=row["user_name"],
                    budget_id=row["budget_id"],
                    budget_name=row["budget_name"],
                    category_id=row["category_id"],
                    category_name=row["category_name"],
                    subcategory_id=row["subcategory_id"],
                    subcategory_name=row["subcategory_name"],
                    subcategory_budget_amount=float(row["subcategory_budget_amount"]) if row["subcategory_budget_amount"] is not None else None,
                    pattern_id=row["pattern_id"],
                    pattern_text=row["pattern_text"]
                )
                for row in results[1]  # results[1] contains the actual data rows
            ]
        except Exception as e:
            print(f"Error executing SQL query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return []
        
    @strawberry.field(name="userTransactions")
    async def user_transactions(
        self, 
        userId: int,
        yearMonth: Optional[str] = None
    ) -> List[TransactionData]:
        """ 
        Obtener todas las transacciones de un usuario con datos relacionados,
        opcionalmente filtradas por mes
        
        Args:
            userId: ID del usuario
            yearMonth: Filtro opcional por año-mes en formato YYYY-MM (ej: 2023-11)
        """
        # Obtener las transacciones filtrando por los user_banks del usuario
        user_banks = await UserBankModel.filter(user_id=userId)
        user_bank_ids = [ub.id for ub in user_banks]
        
        # Construir la consulta base
        query = TransactionModel.filter(
            user_bank_id__in=user_bank_ids
        )
        
        # Aplicar filtro por mes si se especificó
        if yearMonth:
            try:
                year, month = map(int, yearMonth.split('-'))
                # Validar el formato de año-mes
                if not (1 <= month <= 12 and 1000 <= year <= 9999):
                    raise ValueError("Invalid month format")
                
                # Filtrar transacciones por año y mes
                query = query.filter(
                    transaction_date__year=year,
                    transaction_date__month=month
                )
            except (ValueError, TypeError) as e:
                print(f"Error parsing yearMonth parameter: {e}")
                # Si hay error en el formato, ignorar el filtro pero loguear
        
        # Realizar la consulta con las relaciones necesarias
        transactions = await query.prefetch_related(
            'user_bank', 
            'user_bank__bank', 
            'subcategory',
            'subcategory__category'
        )
        
        result = []
        for transaction in transactions:
            result.append(
                TransactionData(
                    id=transaction.id,
                    transaction_date=str(transaction.transaction_date),
                    description=transaction.description,
                    amount=float(transaction.amount),
                    type=transaction.type.value,
                    user_bank_id=transaction.user_bank_id,
                    subcategory_id=transaction.subcategory_id,
                    created_at=str(transaction.created_at),
                    updated_at=str(transaction.updated_at),
                    
                    # Datos relacionados
                    user_bank_name=transaction.user_bank.description or f"Account {transaction.user_bank_id}",
                    bank_name=transaction.user_bank.bank.name,
                    subcategory_name=transaction.subcategory.name,
                    category_name=transaction.subcategory.category.name
                )
            )
        
        return result

schema = strawberry.Schema(query=Query)
