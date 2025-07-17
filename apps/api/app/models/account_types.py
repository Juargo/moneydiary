from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import relationship
from .base import Base

class AccountType(Base):
    __tablename__ = 'account_types'
    __table_args__ = {'schema': 'app'}
    
    id = Column(Integer, primary_key=True, autoincrement=True) # ID del tipo de cuenta
    code = Column(String(20), nullable=False, unique=True) # Código del tipo de cuenta
    name = Column(String, nullable=False) # Nombre del tipo de cuenta
    description = Column(String) # Descripción del tipo de cuenta
    created_at = Column(TIMESTAMP, default=func.current_timestamp()) # Fecha de creación del tipo de cuenta
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()) # Fecha de última actualización del tipo de cuenta

    # ============================
    # Relationships and Foreign Keys
    # ============================
    accounts = relationship("Account", back_populates="account_type")
