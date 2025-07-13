from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import csv
import io

from ...database import get_db
from ...schemas.transactions import (
    TransactionCreateRequest, 
    TransactionUpdateRequest, 
    TransactionResponse,
    TransactionImportResponse
)
from ...services.transaction_service import (
    create_transaction,
    update_transaction,
    get_user_transaction,
    delete_transaction,
    get_user_transactions,
    import_transactions_from_csv,
    import_transactions_from_excel
)
from ...utils.fastapi_auth import get_current_user
from ...models.users import User

# Crear el router
router = APIRouter()

# @router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
# async def create_transaction_endpoint(
#     transaction_data: TransactionCreateRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Crea una nueva transacción para el usuario autenticado"""
#     try:
#         new_transaction = create_transaction(db, current_user.id, transaction_data)
        
#         return TransactionResponse(
#             id=new_transaction.id,
#             amount=float(new_transaction.amount),
#             description=new_transaction.description,
#             notes=new_transaction.notes,
#             transaction_date=new_transaction.transaction_date,
#             account_id=new_transaction.account_id,
#             transfer_account_id=new_transaction.transfer_account_id,
#             category_id=new_transaction.category_id,
#             subcategory_id=new_transaction.subcategory_id,
#             envelope_id=new_transaction.envelope_id,
#             status_id=new_transaction.status_id,
#             is_recurring=new_transaction.is_recurring,
#             is_planned=new_transaction.is_planned,
#             kakebo_emotion=new_transaction.kakebo_emotion,
#             external_id=new_transaction.external_id,
#             user_id=new_transaction.user_id,
#             created_at=new_transaction.created_at.isoformat() if new_transaction.created_at else "",
#             updated_at=new_transaction.updated_at.isoformat() if new_transaction.updated_at else ""
#         )
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#     except Exception as e:
#         print(f"Error creating transaction: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error interno del servidor"
#         )

# @router.get("", response_model=List[TransactionResponse])
# async def get_transactions_endpoint(
#     account_id: Optional[int] = None,
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     category_id: Optional[int] = None,
#     skip: int = 0,
#     limit: int = 50,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Obtiene las transacciones del usuario autenticado con filtros opcionales"""
#     try:
#         transactions = get_user_transactions(
#             db, 
#             current_user.id, 
#             account_id=account_id,
#             start_date=start_date,
#             end_date=end_date,
#             category_id=category_id,
#             skip=skip,
#             limit=limit
#         )
        
#         return [
#             TransactionResponse(
#                 id=t.id,
#                 amount=float(t.amount),
#                 description=t.description,
#                 notes=t.notes,
#                 transaction_date=t.transaction_date,
#                 account_id=t.account_id,
#                 transfer_account_id=t.transfer_account_id,
#                 category_id=t.category_id,
#                 subcategory_id=t.subcategory_id,
#                 envelope_id=t.envelope_id,
#                 status_id=t.status_id,
#                 is_recurring=t.is_recurring,
#                 is_planned=t.is_planned,
#                 kakebo_emotion=t.kakebo_emotion,
#                 external_id=t.external_id,
#                 user_id=t.user_id,
#                 created_at=t.created_at.isoformat() if t.created_at else "",
#                 updated_at=t.updated_at.isoformat() if t.updated_at else ""
#             ) for t in transactions
#         ]
#     except Exception as e:
#         print(f"Error getting transactions: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error interno del servidor"
#         )

# @router.get("/{transaction_id}", response_model=TransactionResponse)
# async def get_transaction_endpoint(
#     transaction_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Obtiene una transacción específica del usuario autenticado"""
#     transaction = get_user_transaction(db, current_user.id, transaction_id)
    
#     if not transaction:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Transacción no encontrada"
#         )
    
#     return TransactionResponse(
#         id=transaction.id,
#         amount=float(transaction.amount),
#         description=transaction.description,
#         notes=transaction.notes,
#         transaction_date=transaction.transaction_date,
#         account_id=transaction.account_id,
#         transfer_account_id=transaction.transfer_account_id,
#         category_id=transaction.category_id,
#         subcategory_id=transaction.subcategory_id,
#         envelope_id=transaction.envelope_id,
#         status_id=transaction.status_id,
#         is_recurring=transaction.is_recurring,
#         is_planned=transaction.is_planned,
#         kakebo_emotion=transaction.kakebo_emotion,
#         external_id=transaction.external_id,
#         user_id=transaction.user_id,
#         created_at=transaction.created_at.isoformat() if transaction.created_at else "",
#         updated_at=transaction.updated_at.isoformat() if transaction.updated_at else ""
#     )

# @router.put("/{transaction_id}", response_model=TransactionResponse)
# async def update_transaction_endpoint(
#     transaction_id: int,
#     transaction_data: TransactionUpdateRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Actualiza una transacción existente del usuario autenticado"""
#     try:
#         updated_transaction = update_transaction(db, current_user.id, transaction_id, transaction_data)
        
#         if not updated_transaction:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Transacción no encontrada"
#             )
        
#         return TransactionResponse(
#             id=updated_transaction.id,
#             amount=float(updated_transaction.amount),
#             description=updated_transaction.description,
#             notes=updated_transaction.notes,
#             transaction_date=updated_transaction.transaction_date,
#             account_id=updated_transaction.account_id,
#             transfer_account_id=updated_transaction.transfer_account_id,
#             category_id=updated_transaction.category_id,
#             subcategory_id=updated_transaction.subcategory_id,
#             envelope_id=updated_transaction.envelope_id,
#             status_id=updated_transaction.status_id,
#             is_recurring=updated_transaction.is_recurring,
#             is_planned=updated_transaction.is_planned,
#             kakebo_emotion=updated_transaction.kakebo_emotion,
#             external_id=updated_transaction.external_id,
#             user_id=updated_transaction.user_id,
#             created_at=updated_transaction.created_at.isoformat() if updated_transaction.created_at else "",
#             updated_at=updated_transaction.updated_at.isoformat() if updated_transaction.updated_at else ""
#         )
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#     except Exception as e:
#         print(f"Error updating transaction: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error interno del servidor"
#         )

# @router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_transaction_endpoint(
#     transaction_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Elimina una transacción del usuario autenticado"""
#     success = delete_transaction(db, current_user.id, transaction_id)
    
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Transacción no encontrada"
#         )

@router.post("/import-csv", response_model=TransactionImportResponse)
async def import_csv_endpoint(
    account_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importa transacciones desde un archivo CSV"""
    try:
        # Validar tipo de archivo
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser un CSV"
            )
        
        # Leer contenido del archivo
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Procesar CSV
        result = import_transactions_from_csv(
            db, 
            current_user.id, 
            account_id, 
            csv_content, 
            file.filename
        )
        
        return TransactionImportResponse(
            total_records=result['total_records'],
            successful_imports=result['successful_imports'],
            failed_imports=result['failed_imports'],
            errors=result['errors']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error importing CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando archivo CSV: {str(e)}"
        )
        
@router.post("/import-excel", response_model=TransactionImportResponse)
async def import_excel_endpoint(
    account_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importa transacciones desde un archivo Excel (xlsx/xls)"""
    try:
        # Validar tipo de archivo
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser Excel (.xlsx o .xls)"
            )
        
        # Leer contenido del archivo
        content = await file.read()
        
        # Procesar Excel
        result = import_transactions_from_excel(
            db, 
            current_user.id, 
            account_id, 
            content, 
            file.filename
        )
        
        return TransactionImportResponse(
            total_records=result['total_records'],
            successful_imports=result['successful_imports'],
            failed_imports=result['failed_imports'],
            errors=result['errors']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error importing Excel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando archivo Excel: {str(e)}"
        )