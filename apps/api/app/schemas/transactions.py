from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict
from datetime import date
from decimal import Decimal

class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: date
    account_id: int
    transfer_account_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    envelope_id: Optional[int] = None
    status_id: int = 1  # Por defecto "completada"
    is_recurring: bool = False
    is_planned: bool = False
    kakebo_emotion: Optional[str] = None
    external_id: Optional[str] = None

class TransactionCreateRequest(TransactionBase):
    @field_validator('amount')
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError('El monto no puede ser cero')
        return v

    @field_validator('kakebo_emotion')
    def validate_kakebo_emotion(cls, v):
        if v and v not in ['joy', 'satisfaction', 'regret', 'worry']:
            raise ValueError('Emoción kakebo no válida')
        return v

class TransactionUpdateRequest(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: Optional[date] = None
    transfer_account_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    envelope_id: Optional[int] = None
    status_id: Optional[int] = None
    is_recurring: Optional[bool] = None
    is_planned: Optional[bool] = None
    kakebo_emotion: Optional[str] = None
    external_id: Optional[str] = None

    @field_validator('amount')
    def validate_amount(cls, v):
        if v is not None and v == 0:
            raise ValueError('El monto no puede ser cero')
        return v

    @field_validator('kakebo_emotion')
    def validate_kakebo_emotion(cls, v):
        if v and v not in ['joy', 'satisfaction', 'regret', 'worry']:
            raise ValueError('Emoción kakebo no válida')
        return v

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True

class TransactionImportResponse(BaseModel):
    total_records: int
    successful_imports: int
    failed_imports: int
    errors: List[str]

class TransactionPreviewItem(BaseModel):
    """Representa una transacción en preview antes de ser confirmada"""
    row_number: int
    amount: Optional[float] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: Optional[date] = None
    account_id: Optional[int] = None
    transfer_account_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    envelope_id: Optional[int] = None
    status_id: Optional[int] = None
    is_recurring: Optional[bool] = False
    is_planned: Optional[bool] = False
    kakebo_emotion: Optional[str] = None
    external_id: Optional[str] = None
    # Campos para mostrar información adicional en el preview
    account_name: Optional[str] = None
    subcategory_name: Optional[str] = None
    # Estado de validación
    is_valid: bool = True
    validation_errors: List[str] = []
    # Datos originales del archivo para referencia
    raw_data: dict = {}

class TransactionPreviewResponse(BaseModel):
    """Respuesta de previsualización de importación"""
    preview_id: str  # ID único para esta previsualización
    total_records: int
    valid_transactions: int
    invalid_transactions: int
    account_id: int
    account_name: str
    profile_name: str
    transactions: List[TransactionPreviewItem]
    global_errors: List[str] = []

class TransactionPreviewConfirmRequest(BaseModel):
    """Request para confirmar la importación después del preview"""
    preview_id: str
    selected_transactions: Optional[List[int]] = None  # Números de fila a importar, si None importa todas las válidas
    modifications: Optional[Dict[int, TransactionPreviewItem]] = None  # Modificaciones por número de fila