from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class AccountCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la cuenta")
    account_number: Optional[str] = Field(None, max_length=50, description="Número de cuenta")
    bank_id: int = Field(..., gt=0, description="ID del banco")
    account_type_id: int = Field(..., gt=0, description="ID del tipo de cuenta")
    current_balance: Decimal = Field(0, description="Saldo actual")
    active: bool = Field(True, description="Si la cuenta está activa")

class AccountUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la cuenta")
    account_number: Optional[str] = Field(None, max_length=50, description="Número de cuenta")
    bank_id: Optional[int] = Field(None, gt=0, description="ID del banco")
    account_type_id: Optional[int] = Field(None, gt=0, description="ID del tipo de cuenta")
    current_balance: Optional[Decimal] = Field(None, description="Saldo actual")
    active: Optional[bool] = Field(None, description="Si la cuenta está activa")

class AccountResponse(BaseModel):
    id: int
    name: str
    account_number: Optional[str]
    bank_id: int
    account_type_id: int
    current_balance: Decimal
    active: bool
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True