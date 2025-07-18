from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ImportFileType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    XLS = "xls"
    XLSX = "xlsx"

class ImportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FileColumnMappingBase(BaseModel):
    source_column_name: str
    source_column_index: Optional[int] = None
    target_field_name: str
    is_required: bool = True
    position: Optional[int] = None
    transformation_rule: Optional[str] = None
    default_value: Optional[str] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    regex_pattern: Optional[str] = None

class FileColumnMappingCreate(FileColumnMappingBase):
    @field_validator('target_field_name')
    def validate_target_field(cls, v):
        valid_fields = ['date', 'amount', 'description', 'notes', 'category', 'reference', 'account_number']
        if v not in valid_fields:
            raise ValueError(f'Campo objetivo debe ser uno de: {", ".join(valid_fields)}')
        return v

class FileColumnMappingResponse(FileColumnMappingBase):
    id: int
    profile_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class FileImportProfileBase(BaseModel):
    name: str
    description: Optional[str] = None
    account_id: int
    is_default: bool = False
    
    # Configuración para archivos delimitados (CSV, algunos Excel)
    delimiter: str = ","
    has_header: bool = True
    encoding: str = "utf-8"
    
    # Configuración de formato
    date_format: str = "DD/MM/YYYY"
    decimal_separator: str = "."
    
    # Configuración específica para Excel
    sheet_name: Optional[str] = None
    header_row: int = 1
    start_row: int = 2
    skip_empty_rows: bool = True
    auto_detect_format: bool = True

class FileImportProfileCreate(FileImportProfileBase):
    column_mappings: List[FileColumnMappingCreate] = []
    
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
    
    @field_validator('header_row')
    def validate_header_row(cls, v):
        if v < 1:
            raise ValueError('La fila de encabezados debe ser mayor a 0')
        return v
    
    @field_validator('start_row')
    def validate_start_row(cls, v):
        if v < 1:
            raise ValueError('La fila de inicio debe ser mayor a 0')
        return v

class FileImportProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    delimiter: Optional[str] = None
    has_header: Optional[bool] = None
    date_format: Optional[str] = None
    decimal_separator: Optional[str] = None
    encoding: Optional[str] = None
    sheet_name: Optional[str] = None
    header_row: Optional[int] = None
    start_row: Optional[int] = None
    skip_empty_rows: Optional[bool] = None
    auto_detect_format: Optional[bool] = None
    column_mappings: Optional[List[FileColumnMappingCreate]] = None

class FileImportProfileResponse(FileImportProfileBase):
    id: int
    user_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    column_mappings: List[FileColumnMappingResponse] = []
    
    class Config:
        from_attributes = True

class FileImportResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: ImportFileType
    file_size: Optional[int]
    record_count: int
    success_count: int
    error_count: int
    duplicate_count: int
    status: ImportStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: Optional[datetime]
    profile_name: str
    bank_name: str
    account_name: str
    
    class Config:
        from_attributes = True

class ImportHistoryResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: ImportFileType
    file_size: Optional[int]
    record_count: int
    success_count: int
    error_count: int
    duplicate_count: int
    status: ImportStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: Optional[datetime]
    profile_name: str
    bank_name: str
    account_name: str
    
    class Config:
        from_attributes = True

class ImportErrorResponse(BaseModel):
    id: int
    import_id: int
    row_number: Optional[int]
    column_name: Optional[str]
    error_type: str
    error_message: str
    raw_data: Optional[str]
    suggested_fix: Optional[str]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ImportValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    preview_data: Optional[List[dict]] = None
    detected_columns: Optional[List[str]] = None
    suggested_mappings: Optional[List[dict]] = None

class ImportProgressResponse(BaseModel):
    import_id: int
    status: ImportStatus
    progress_percentage: float
    current_row: Optional[int]
    total_rows: Optional[int]
    estimated_time_remaining: Optional[int]  # En segundos
    message: Optional[str]

class BulkImportRequest(BaseModel):
    profile_id: int
    account_id: int
    files: List[str]  # Lista de nombres de archivos subidos
    overwrite_duplicates: bool = False
    skip_validation: bool = False

class ProfileStatisticsResponse(BaseModel):
    profile_name: str
    total_imports: int
    successful_imports: int
    failed_imports: int
    success_rate: float
    total_transactions_imported: int
    last_import_date: Optional[datetime]
    is_default: bool
    bank_name: Optional[str]
    average_processing_time: Optional[float]  # En segundos
    most_common_errors: List[dict] = []
    
    class Config:
        from_attributes = True

# Schemas para compatibilidad con código existente (deprecated)
class CsvColumnMappingBase(FileColumnMappingBase):
    """Deprecated: Use FileColumnMappingBase instead"""
    pass

class CsvColumnMappingCreate(FileColumnMappingCreate):
    """Deprecated: Use FileColumnMappingCreate instead"""
    pass

class CsvColumnMappingResponse(FileColumnMappingResponse):
    """Deprecated: Use FileColumnMappingResponse instead"""
    pass

class CsvImportProfileBase(FileImportProfileBase):
    """Deprecated: Use FileImportProfileBase instead"""
    pass

class CsvImportProfileCreate(FileImportProfileCreate):
    """Deprecated: Use FileImportProfileCreate instead"""
    pass

class CsvImportProfileUpdate(FileImportProfileUpdate):
    """Deprecated: Use FileImportProfileUpdate instead"""
    pass

class CsvImportProfileResponse(FileImportProfileResponse):
    """Deprecated: Use FileImportProfileResponse instead"""
    pass

# Schemas de configuración para diferentes tipos de archivo
class ExcelImportConfig(BaseModel):
    """Configuración específica para archivos Excel"""
    sheet_name: Optional[str] = None
    header_row: int = 1
    start_row: int = 2
    max_rows: Optional[int] = None
    skip_empty_rows: bool = True
    auto_detect_types: bool = True
    read_only: bool = True

class CsvImportConfig(BaseModel):
    """Configuración específica para archivos CSV"""
    delimiter: str = ","
    quotechar: str = '"'
    escapechar: Optional[str] = None
    encoding: str = "utf-8"
    skip_blank_lines: bool = True
    comment_prefix: Optional[str] = None

# Schema para preview de datos antes de importar
class ImportPreviewRequest(BaseModel):
    profile_id: int
    filename: str
    preview_rows: int = 10

class ImportPreviewResponse(BaseModel):
    headers: List[str]
    sample_data: List[dict]
    total_rows_detected: int
    file_type: ImportFileType
    encoding_detected: Optional[str]
    delimiter_detected: Optional[str]
    issues_found: List[str] = []
    recommendations: List[str] = []