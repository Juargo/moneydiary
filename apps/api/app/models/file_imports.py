from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Boolean, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base

class ImportFileType(enum.Enum):
    CSV = "CSV"
    EXCEL = "EXCEL"
    XLS = "XLS"
    XLSX = "XLSX"
    
    @classmethod
    def _missing_(cls, value):
        """Permite valores en minúsculas y los convierte a mayúsculas"""
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None

class ImportStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AmountSchemaType(enum.Enum):
    """Define cómo se representan los montos en el archivo"""
    SINGLE_COLUMN = "single_column"  # Una columna con positivos/negativos
    SEPARATE_COLUMNS = "separate_columns"  # Columnas separadas para débito/crédito
    DEBIT_CREDIT = "debit_credit"  # Columnas Débito/Crédito específicas

class TransactionTypeDetection(enum.Enum):
    """Define cómo detectar el tipo de transacción"""
    BY_AMOUNT_SIGN = "by_amount_sign"  # Por signo del monto (positivo/negativo)
    BY_COLUMN_TYPE = "by_column_type"  # Por tipo de columna (débito/crédito)
    BY_EXPLICIT_FIELD = "by_explicit_field"  # Por campo explícito en el archivo

class FileImport(Base):
    __tablename__ = 'file_imports'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True) # ID del import
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # ID del usuario que realiza el import
    profile_id = Column(Integer, ForeignKey('file_import_profiles.id'), nullable=False) # Perfil de importación utilizado
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)  # Cuenta destino
    filename = Column(String, nullable=False) # Nombre del archivo importado
    original_filename = Column(String, nullable=False) # Nombre original del archivo importado
    file_type = Column(Enum(ImportFileType), nullable=False)  # csv, excel, xls, xlsx
    file_size = Column(Integer)  # Tamaño en bytes
    record_count = Column(Integer, nullable=False, default=0) # Número de registros en el archivo importado
    success_count = Column(Integer, nullable=False, default=0) # Número de registros procesados con éxito
    error_count = Column(Integer, nullable=False, default=0) # Número de registros con errores
    duplicate_count = Column(Integer, nullable=False, default=0) # Número de registros duplicados
    status = Column(Enum(ImportStatus), nullable=False, default=ImportStatus.PENDING) # Estado del import
    started_at = Column(TIMESTAMP) # Fecha y hora de inicio del import
    completed_at = Column(TIMESTAMP) # Fecha y hora de finalización del import
    created_at = Column(TIMESTAMP) # Fecha y hora de creación del registro
    updated_at = Column(TIMESTAMP) # Fecha y hora de última actualización del registro

    # ============================
    # Relationships and Foreign Keys
    # ============================
    user = relationship("User", back_populates="file_imports") # Relación con el usuario que realiza el import
    profile = relationship("FileImportProfile", back_populates="file_imports") # Relación con el perfil de importación utilizado
    account = relationship("Account") # Relación con la cuenta destino del import
    transactions = relationship("Transaction", back_populates="import_data") # Transacciones asociadas al import

class FileImportProfile(Base):
    __tablename__ = 'file_import_profiles'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, nullable=False, default=False)
    file_type = Column(Enum(ImportFileType), nullable=False, default=ImportFileType.CSV)  # Tipo de archivo esperado
    
    # Configuración para archivos delimitados (CSV, algunos Excel)
    delimiter = Column(String(1), nullable=False, default=",")
    has_header = Column(Boolean, nullable=False, default=True)
    
    # Configuración de formato
    date_format = Column(String, nullable=False, default="YYYY-MM-DD")
    decimal_separator = Column(String(1), nullable=False, default=".")
    encoding = Column(String, default="utf-8")  # Para archivos CSV
    
    # Configuración de esquema de montos
    amount_schema = Column(Enum(AmountSchemaType), nullable=False, default=AmountSchemaType.SINGLE_COLUMN)
    transaction_type_detection = Column(Enum(TransactionTypeDetection), nullable=False, default=TransactionTypeDetection.BY_AMOUNT_SIGN)
    
    # Para esquema de columna única (positivos/negativos)
    # Se mapea en column_mappings con target_field_name = "amount"
    
    # Para esquemas de columnas separadas
    # Se definen mapeos específicos:
    # - "debit_amount" -> columna de débitos/egresos
    # - "credit_amount" -> columna de créditos/ingresos
    # - "transaction_type" -> columna que indica tipo (opcional)
    
    # Reglas de interpretación
    positive_is_income = Column(Boolean, default=True)  # True: positivo=ingreso, False: positivo=gasto
    debit_column_is_expense = Column(Boolean, default=True)  # True: débito=gasto, False: débito=ingreso
    
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
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('file_import_profiles.id'), nullable=False)
    source_column_name = Column(String, nullable=False)  # Nombre en el archivo
    source_column_index = Column(Integer)  # Índice de columna (para archivos sin header)
    target_field_name = Column(String, nullable=False)  # Campo destino: amount, debit_amount, credit_amount, date, description, etc.
    is_required = Column(Boolean, nullable=False, default=True)
    position = Column(Integer)  # Orden de procesamiento
    
    # Reglas de transformación
    transformation_rule = Column(Text)  # JSON con reglas específicas
    default_value = Column(String)  # Valor por defecto si está vacío
    
    # Para campos de monto - configuración adicional
    amount_multiplier = Column(String, default="1")  # Multiplicador para el monto (ej: "-1" para invertir signo)
    treat_empty_as_zero = Column(Boolean, default=True)  # Si tratar vacíos como 0
    
    # Validaciones
    min_value = Column(String)  # Para números/fechas
    max_value = Column(String)  # Para números/fechas
    regex_pattern = Column(String)  # Para validación de formato
    
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    profile = relationship("FileImportProfile", back_populates="column_mappings")

class ImportError(Base):
    __tablename__ = 'import_errors'
    __table_args__ = {'schema': 'app'}

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

# ============================
# DOCUMENTACIÓN DE ESQUEMAS DE MONTOS
# ============================

"""
ESQUEMAS DE MANEJO DE MONTOS EN ARCHIVOS DE BANCOS:

1. SINGLE_COLUMN (Una columna con positivos/negativos):
   - Mapeo: "amount" -> "Monto" 
   - Lógica: 
     * Si positive_is_income=True: Positivo=Ingreso, Negativo=Gasto
     * Si positive_is_income=False: Positivo=Gasto, Negativo=Ingreso

2. SEPARATE_COLUMNS (Columnas separadas débito/crédito):
   - Mapeo: 
     * "debit_amount" -> "Débito" o "Cargo" o "Egreso"
     * "credit_amount" -> "Crédito" o "Abono" o "Ingreso"
   - Lógica:
     * Si debit_column_is_expense=True: Débito=Gasto, Crédito=Ingreso
     * Si debit_column_is_expense=False: Débito=Ingreso, Crédito=Gasto

3. DEBIT_CREDIT (Igual que SEPARATE_COLUMNS pero con nombres específicos):
   - Similar a SEPARATE_COLUMNS pero con convención contable estricta

DETECCIÓN DE TIPO DE TRANSACCIÓN:

1. BY_AMOUNT_SIGN: Basado en el signo del monto final
2. BY_COLUMN_TYPE: Basado en qué columna tiene valor (débito vs crédito)
3. BY_EXPLICIT_FIELD: Basado en un campo específico del archivo que indica el tipo

CAMPOS TARGET ESPECIALES:
- "amount": Monto principal (para esquema de columna única)
- "debit_amount": Monto de débito
- "credit_amount": Monto de crédito
- "transaction_type": Tipo explícito de transacción
- "date": Fecha de transacción
- "description": Descripción
- "reference": Referencia o número de transacción
- "notes": Notas adicionales
- "category": Categoría (si viene en el archivo)

EJEMPLOS DE USO:

Banco que usa una columna con positivos/negativos:
- amount_schema = SINGLE_COLUMN
- transaction_type_detection = BY_AMOUNT_SIGN
- positive_is_income = False (porque los gastos suelen ser negativos)
- Mapeo: "Monto" -> "amount"

Banco que usa columnas separadas:
- amount_schema = SEPARATE_COLUMNS  
- transaction_type_detection = BY_COLUMN_TYPE
- debit_column_is_expense = True
- Mapeos: 
  * "Débito" -> "debit_amount"
  * "Crédito" -> "credit_amount"

Banco con campo explícito de tipo:
- amount_schema = SINGLE_COLUMN
- transaction_type_detection = BY_EXPLICIT_FIELD
- Mapeos:
  * "Monto" -> "amount"
  * "Tipo" -> "transaction_type"
"""