from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base

class Bank(Base):
    """Modelo para representar bancos en el sistema."""
    
    __tablename__ = "banks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), nullable=False, index=True, unique=True)
    logo_url = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    accounts = relationship("Account", back_populates="bank")
    csv_profiles = relationship("CsvImportProfile", back_populates="bank")
    
    def __repr__(self):
        return f"<Bank {self.name}>"