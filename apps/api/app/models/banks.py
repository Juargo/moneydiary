from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base

class Bank(Base):
    """Modelo para representar bancos en el sistema."""
    
    __tablename__ = "banks"
    __table_args__ = {'schema': 'app'} 

    id = Column(Integer, primary_key=True, index=True) # ID del banco
    name = Column(String(100), nullable=False, index=True) # Nombre del banco
    code = Column(String(20), nullable=False, index=True, unique=True) # Código del banco
    logo_url = Column(String(255), nullable=True) # URL del logo del banco
    active = Column(Boolean, default=True) # Indica si el banco está activo
    description = Column(Text, nullable=True) # Descripción del banco
    created_at = Column(DateTime, default=func.now()) # Fecha de creación del banco
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) # Fecha de última actualización del banco
    
    # ============================
    # Relationships and Foreign Keys
    # ============================
    csv_profiles = relationship("CsvImportProfile", back_populates="bank") # Perfiles de importación CSV asociados al banco
    accounts = relationship("Account", back_populates="bank") # Cuentas asociadas al banco
    
    def __repr__(self):
        return f"<Bank {self.name}>"