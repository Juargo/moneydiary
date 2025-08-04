from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import csv
import io
import logging

from ...database import get_db
from ...schemas.transactions import (
    TransactionCreateRequest, 
    TransactionUpdateRequest, 
    TransactionResponse,
    TransactionImportResponse,
    TransactionPreviewResponse,
    TransactionPreviewConfirmRequest
)
from ...services.transaction_service import (
    create_transaction,
    update_transaction,
    get_user_transaction,
    delete_transaction,
    get_user_transactions,
    import_transactions_from_csv,
    import_transactions_from_excel,
    import_transactions_with_profile,
    preview_transactions_with_profile,
    confirm_transaction_preview
)
from ...utils.fastapi_auth import get_current_user
from ...models.users import User

# Crear el router
router = APIRouter()

# Configurar logger
logger = logging.getLogger(__name__)

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
    profile_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importa transacciones usando un perfil de importación"""
    try:
        # Validar tipo de archivo
        if not file.filename or not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser un CSV"
            )
        
        # Leer contenido del archivo
        content = await file.read()
        
        # Procesar con perfil - CONVERTIR A INT EXPLÍCITAMENTE
        result = import_transactions_with_profile(
            db, 
            getattr(current_user, 'id'),  # Usar getattr para obtener el valor
            profile_id, 
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
        print(f"Error importing CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando archivo CSV: {str(e)}"
        )
        
@router.post("/import-excel", response_model=TransactionImportResponse)
async def import_excel_endpoint(
    profile_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importa transacciones usando un perfil de importación"""
    try:
        # Validar tipo de archivo
        if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser Excel (.xlsx, .xls) o CSV"
            )
        
        # Leer contenido del archivo
        content = await file.read()
        
        # Procesar con perfil - CONVERTIR A INT EXPLÍCITAMENTE
        result = import_transactions_with_profile(
            db, 
            getattr(current_user, 'id'),  # Conversión usando getattr
            profile_id, 
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
    except ValueError as e:
        # Errores de validación o procesamiento de archivo
        error_msg = str(e)
        if "no es un Excel válido" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo '{file.filename}' no es un archivo Excel válido. Verifique que el archivo no esté corrupto."
            )
        elif "Perfil de importación no encontrado" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de importación no encontrado"
            )
        elif "Cuenta no encontrada" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada o no autorizada"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error procesando archivo: {error_msg}"
            )
    except Exception as e:
        logger.error(f"Error importing file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor procesando el archivo"
        )
        
@router.post("/import-excel-with-duplicates")      
async def import_excel_with_duplicate_options(
    account_id: int = Form(...),
    allow_duplicates: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importar transacciones desde Excel con opciones de duplicados"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
    
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel (.xlsx, .xls)")
    
    try:
        file_content = await file.read()
        
        result = import_transactions_from_excel(
            db=db,
            user_id=getattr(current_user, 'id'),
            account_id=account_id,
            file_content=file_content,
            filename=file.filename,
            allow_duplicates=allow_duplicates
        )
        
        return {
            "message": "Importación completada",
            "details": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado en importación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/preview-import", response_model=TransactionPreviewResponse)
async def preview_import_endpoint(
    profile_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Genera una previsualización de las transacciones a importar"""
    try:
        # Validar tipo de archivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo requerido"
            )
        
        filename_lower = file.filename.lower()
        if not filename_lower.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser CSV (.csv) o Excel (.xlsx, .xls)"
            )
        
        # Leer contenido del archivo
        content = await file.read()
        
        # Generar previsualización
        preview = preview_transactions_with_profile(
            db, 
            getattr(current_user, 'id'),
            profile_id, 
            content, 
            file.filename
        )
        
        return TransactionPreviewResponse(**preview)
        
    except HTTPException:
        raise
    except ValueError as e:
        # Errores de validación o procesamiento de archivo
        error_msg = str(e)
        if "no es un Excel válido" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo '{file.filename}' no es un archivo Excel válido. Verifique que el archivo no esté corrupto."
            )
        elif "Perfil de importación no encontrado" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de importación no encontrado"
            )
        elif "Cuenta no encontrada" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada o no autorizada"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error procesando archivo: {error_msg}"
            )
    except Exception as e:
        logger.error(f"Error generando previsualización: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor procesando el archivo"
        )

@router.post("/confirm-import", response_model=TransactionImportResponse)
async def confirm_import_endpoint(
    request: TransactionPreviewConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirma e importa las transacciones desde una previsualización"""
    try:
        # Convertir modifications a diccionarios si es necesario
        modifications_dict = None
        if request.modifications:
            modifications_dict = {}
            for row_num, transaction_item in request.modifications.items():
                # Convertir TransactionPreviewItem a diccionario
                modifications_dict[row_num] = transaction_item.dict() if hasattr(transaction_item, 'dict') else transaction_item
        
        result = confirm_transaction_preview(
            db,
            getattr(current_user, 'id'),
            request.preview_id,
            request.selected_transactions,
            modifications_dict
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
        logger.error(f"Error confirmando importación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error confirmando importación: {str(e)}"
        )