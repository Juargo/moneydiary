from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Boolean, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base

class ImportFileType(enum.Enum):
    CSV = "csv"
    EXCEL = "excel"
    XLS = "xls"
    XLSX = "xlsx"

class ImportStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FileImport(Base):
    __tablename__ = 'file_imports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    profile_id = Column(Integer, ForeignKey('file_import_profiles.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)  # Cuenta destino
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(Enum(ImportFileType), nullable=False)  # csv, excel, xls, xlsx
    file_size = Column(Integer)  # Tamaño en bytes
    record_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    duplicate_count = Column(Integer, nullable=False, default=0)
    status = Column(Enum(ImportStatus), nullable=False, default=ImportStatus.PENDING)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="file_imports")
    profile = relationship("FileImportProfile", back_populates="file_imports")
    account = relationship("Account")
    transactions = relationship("Transaction", back_populates="import_data")

class FileImportProfile(Base):
    __tablename__ = 'file_import_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, nullable=False, default=False)
    
    # Configuración para archivos delimitados (CSV, algunos Excel)
    delimiter = Column(String(1), nullable=False, default=",")
    has_header = Column(Boolean, nullable=False, default=True)
    
    # Configuración de formato
    date_format = Column(String, nullable=False, default="YYYY-MM-DD")
    decimal_separator = Column(String(1), nullable=False, default=".")
    encoding = Column(String, default="utf-8")  # Para archivos CSV
    
    # Configuración específica para Excel
    sheet_name = Column(String)  # Nombre de la hoja a importar (None = primera hoja)
    header_row = Column(Integer, default=1)  # Fila donde están los headers
    start_row = Column(Integer, default=2)  # Fila donde empiezan los datos
    
    # Configuración avanzada
    skip_empty_rows = Column(Boolean, default=True)
    auto_detect_format = Column(Boolean, default=True)  # Auto-detectar fechas, números, etc.
    
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="file_import_profiles")
    account = relationship("Account", back_populates="import_profiles")
    file_imports = relationship("FileImport", back_populates="profile")
    column_mappings = relationship("FileColumnMapping", back_populates="profile")

class FileColumnMapping(Base):
    __tablename__ = 'file_column_mappings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('file_import_profiles.id'), nullable=False)
    source_column_name = Column(String, nullable=False)  # Nombre en el archivo
    source_column_index = Column(Integer)  # Índice de columna (para archivos sin header)
    target_field_name = Column(String, nullable=False)  # Campo destino en Transaction
    is_required = Column(Boolean, nullable=False, default=True)
    position = Column(Integer)  # Orden de procesamiento
    
    # Reglas de transformación
    transformation_rule = Column(Text)  # JSON con reglas específicas
    default_value = Column(String)  # Valor por defecto si está vacío
    
    # Validaciones
    min_value = Column(String)  # Para números/fechas
    max_value = Column(String)  # Para números/fechas
    regex_pattern = Column(String)  # Para validación de formato
    
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    profile = relationship("FileImportProfile", back_populates="column_mappings")

class ImportError(Base):
    __tablename__ = 'import_errors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    import_id = Column(Integer, ForeignKey('file_imports.id'), nullable=False)
    row_number = Column(Integer)
    column_name = Column(String)  # Columna donde ocurrió el error
    error_type = Column(String)  # validation, transformation, format, etc.
    error_message = Column(Text, nullable=False)
    raw_data = Column(Text)  # Datos originales de la fila
    suggested_fix = Column(Text)  # Sugerencia de corrección
    created_at = Column(TIMESTAMP)

    import_data = relationship("FileImport", backref="errors")