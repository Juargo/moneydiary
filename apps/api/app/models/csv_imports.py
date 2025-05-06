from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base

class CsvImport(Base):
    __tablename__ = 'csv_imports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    profile_id = Column(Integer, ForeignKey('csv_import_profiles.id'), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    record_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    duplicate_count = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False) 
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="csv_imports")
    profile = relationship("CsvImportProfile", back_populates="csv_imports")
    transactions = relationship("Transaction", back_populates="import_data")

class CsvImportProfile(Base):
    __tablename__ = 'csv_import_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, nullable=False, default=False)
    delimiter = Column(String(1), nullable=False, default=",")
    has_header = Column(Boolean, nullable=False, default=True)
    date_format = Column(String, nullable=False, default="YYYY-MM-DD")
    decimal_separator = Column(String(1), nullable=False, default=".")
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="csv_import_profiles")
    bank = relationship("Bank", back_populates="csv_profiles")
    csv_imports = relationship("CsvImport", back_populates="profile")
    column_mappings = relationship("CsvColumnMapping", back_populates="profile")

class CsvColumnMapping(Base):
    __tablename__ = 'csv_column_mappings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('csv_import_profiles.id'), nullable=False)
    source_column_name = Column(String, nullable=False)
    target_field_name = Column(String, nullable=False)
    is_required = Column(Boolean, nullable=False, default=True)
    position = Column(Integer)
    transformation_rule = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    profile = relationship("CsvImportProfile", back_populates="column_mappings")

class ImportError(Base):
    __tablename__ = 'import_errors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    import_id = Column(Integer, ForeignKey('csv_imports.id'), nullable=False)
    row_number = Column(Integer)
    error_message = Column(Text, nullable=False)
    raw_data = Column(Text)
    created_at = Column(TIMESTAMP)

    import_data = relationship("CsvImport", backref="errors")
