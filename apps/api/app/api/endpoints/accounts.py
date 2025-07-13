from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...schemas.accounts import AccountCreateRequest, AccountUpdateRequest, AccountResponse
from ...services.account_service import create_account, update_account, get_user_account, delete_account
from ...utils.fastapi_auth import get_current_user  
from ...models.users import User

# Crear el router con prefijo correcto
router = APIRouter()

@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account_endpoint(
    account_data: AccountCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una nueva cuenta para el usuario autenticado"""
    try:
        new_account = create_account(db, current_user.id, account_data)  # Usar función directa
        
        # Convertir a formato de respuesta
        return AccountResponse(
            id=new_account.id,
            name=new_account.name,
            account_number=new_account.account_number,
            bank_id=new_account.bank_id,
            account_type_id=new_account.account_type_id,
            current_balance=new_account.current_balance,
            active=new_account.active,
            user_id=new_account.user_id,
            created_at=new_account.created_at.isoformat() if new_account.created_at else "",
            updated_at=new_account.updated_at.isoformat() if new_account.updated_at else ""
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error creating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account_endpoint(
    account_id: int,
    account_data: AccountUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza una cuenta existente del usuario autenticado"""
    try:
        updated_account = update_account(db, current_user.id, account_id, account_data)  # Usar función directa
        
        if not updated_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada"
            )
        
        return AccountResponse(
            id=updated_account.id,
            name=updated_account.name,
            account_number=updated_account.account_number,
            bank_id=updated_account.bank_id,
            account_type_id=updated_account.account_type_id,
            current_balance=updated_account.current_balance,
            active=updated_account.active,
            user_id=updated_account.user_id,
            created_at=updated_account.created_at.isoformat() if updated_account.created_at else "",
            updated_at=updated_account.updated_at.isoformat() if updated_account.updated_at else ""
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error updating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account_endpoint(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una cuenta específica del usuario autenticado"""
    account = get_user_account(db, current_user.id, account_id)  # Usar función directa
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta no encontrada"
        )
    
    return AccountResponse(
        id=account.id,
        name=account.name,
        account_number=account.account_number,
        bank_id=account.bank_id,
        account_type_id=account.account_type_id,
        current_balance=account.current_balance,
        active=account.active,
        user_id=account.user_id,
        created_at=account.created_at.isoformat() if account.created_at else "",
        updated_at=account.updated_at.isoformat() if account.updated_at else ""
    )

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account_endpoint(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina (desactiva) una cuenta del usuario autenticado"""
    success = delete_account(db, current_user.id, account_id)  # Usar función directa
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta no encontrada"
        )