from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List, Optional
from decimal import Decimal

from ..models.accounts import Account
from ..models.banks import Bank
from ..models.account_types import AccountType
from ..schemas.accounts import AccountCreateRequest, AccountUpdateRequest


def get_user_accounts(db: Session, user_id: int) -> List[Account]:
    """Obtiene todas las cuentas activas de un usuario"""
    # Load accounts with related account_type and bank data
    result = db.execute(
        select(Account)
        .options(
            joinedload(Account.account_type),
            joinedload(Account.bank)
        )
        .where(
            Account.user_id == user_id,
            Account.active == True
        )
    )
    return result.scalars().unique().all()


def get_user_account_by_id(db: Session, user_id: int, account_id: int) -> Optional[Account]:
    """Obtiene una cuenta específica del usuario por ID con sus relaciones"""
    try:
        result = db.execute(
            select(Account)
            .options(joinedload(Account.bank))
            .options(joinedload(Account.account_type))
            .where(
                Account.id == account_id,
                Account.user_id == user_id,
            Account.active == True
            )
        )
        return result.scalar_one_or_none()
    except Exception as e:
        print(f"Error al obtener cuenta {account_id}: {e}")
        return None
    
class AccountService:
    @staticmethod
    def create_account(db: Session, user_id: int, account_data: AccountCreateRequest) -> Account:
        """Crea una nueva cuenta para el usuario"""
        
        # Verificar que el banco existe
        bank = db.execute(select(Bank).where(Bank.id == account_data.bank_id)).scalar_one_or_none()
        if not bank:
            raise ValueError("El banco especificado no existe")
        
        # Verificar que el tipo de cuenta existe
        account_type = db.execute(select(AccountType).where(AccountType.id == account_data.account_type_id)).scalar_one_or_none()
        if not account_type:
            raise ValueError("El tipo de cuenta especificado no existe")
        
        # Crear la cuenta
        new_account = Account(
            name=account_data.name,
            account_number=account_data.account_number,
            bank_id=account_data.bank_id,
            account_type_id=account_data.account_type_id,
            current_balance=account_data.current_balance,
            active=account_data.active,
            user_id=user_id
        )
        
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        
        return new_account
    
    @staticmethod
    def update_account(db: Session, user_id: int, account_id: int, account_data: AccountUpdateRequest) -> Optional[Account]:
        """Actualiza una cuenta existente del usuario"""
        
        # Obtener la cuenta y verificar que pertenece al usuario
        account = db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id
            )
        ).scalar_one_or_none()
        
        if not account:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = account_data.dict(exclude_unset=True)
        
        # Verificar banco si se está actualizando
        if 'bank_id' in update_data:
            bank = db.execute(select(Bank).where(Bank.id == update_data['bank_id'])).scalar_one_or_none()
            if not bank:
                raise ValueError("El banco especificado no existe")
        
        # Verificar tipo de cuenta si se está actualizando
        if 'account_type_id' in update_data:
            account_type = db.execute(select(AccountType).where(AccountType.id == update_data['account_type_id'])).scalar_one_or_none()
            if not account_type:
                raise ValueError("El tipo de cuenta especificado no existe")
        
        # Mapear current_balance a balance
        if 'current_balance' in update_data:
            update_data['current_balance'] = update_data.pop('current_balance')
        
        # Mapear active a active
        if 'active' in update_data:
            update_data['active'] = update_data.pop('active')
        
        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(account, field, value)
        
        db.commit()
        db.refresh(account)
        
        return account
    
    @staticmethod
    def get_user_account(db: Session, user_id: int, account_id: int) -> Optional[Account]:
        """Obtiene una cuenta específica del usuario"""
        return db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id
            )
        ).scalar_one_or_none()
    
    @staticmethod
    def delete_account(db: Session, user_id: int, account_id: int) -> bool:
        """Elimina (desactiva) una cuenta del usuario"""
        account = db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id
            )
        ).scalar_one_or_none()
        
        if not account:
            return False
        
        # En lugar de eliminar, desactivar la cuenta
        account.active = False
        db.commit()
        
        return True