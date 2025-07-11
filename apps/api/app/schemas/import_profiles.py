from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

class CsvColumnMappingBase(BaseModel):
    source_column_name: str
    target_field_name: str
    is_required: bool = True
    position: Optional[int] = None
    transformation_rule: Optional[str] = None

class CsvColumnMappingCreate(CsvColumnMappingBase):
    @field_validator('target_field_name')
    def validate_target_field(cls, v):
        valid_fields = ['date', 'amount', 'description', 'notes', 'category', 'reference']
        if v not in valid_fields:
            raise ValueError(f'Campo objetivo debe ser uno de: {", ".join(valid_fields)}')
        return v

class CsvColumnMappingResponse(CsvColumnMappingBase):
    id: int
    profile_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True

class CsvImportProfileBase(BaseModel):
    name: str
    description: Optional[str] = None
    bank_id: int
    is_default: bool = False
    delimiter: str = ","
    has_header: bool = True
    date_format: str = "YYYY-MM-DD"
    decimal_separator: str = "."

class CsvImportProfileCreate(CsvImportProfileBase):
    column_mappings: List[CsvColumnMappingCreate] = []
    
    @field_validator('delimiter')
    def validate_delimiter(cls, v):
        if v not in [',', ';', '\t', '|']:
            raise ValueError('Delimitador debe ser uno de: , ; \\t |')
        return v
    
    @field_validator('decimal_separator')
    def validate_decimal_separator(cls, v):
        if v not in ['.', ',']:
            raise ValueError('Separador decimal debe ser . o ,')
        return v

class CsvImportProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    delimiter: Optional[str] = None
    has_header: Optional[bool] = None
    date_format: Optional[str] = None
    decimal_separator: Optional[str] = None
    column_mappings: Optional[List[CsvColumnMappingCreate]] = None

class CsvImportProfileResponse(CsvImportProfileBase):
    id: int
    user_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    column_mappings: List[CsvColumnMappingResponse] = []
    
    class Config:
        orm_mode = True

class ImportHistoryResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    record_count: int
    success_count: int
    error_count: int
    duplicate_count: int
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: Optional[datetime]
    profile_name: str
    bank_name: str
    
    class Config:
        orm_mode = True