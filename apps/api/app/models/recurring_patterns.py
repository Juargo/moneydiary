from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, TIMESTAMP, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class RecurringPattern(Base):
    __tablename__ = 'recurring_patterns'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    frequency = Column(String, nullable=False)  # daily, weekly, monthly, yearly
    day_of_month = Column(Integer)  # for monthly patterns
    day_of_week = Column(Integer)   # for weekly patterns
    month = Column(Integer)         # for yearly patterns
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="recurring_patterns")
    transactions = relationship("Transaction", back_populates="recurring_pattern")


class DescriptionPattern(Base):
    """
    Modelo para patrones que transforman descripciones de transacciones en subcategorías
    """
    __tablename__ = 'description_patterns'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)  # Nombre descriptivo del patrón
    pattern = Column(String, nullable=False)  # Patrón de texto a buscar (regex o texto simple)
    pattern_type = Column(String, nullable=False, default='contains')  # 'contains', 'starts_with', 'ends_with', 'regex', 'exact'
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False)
    priority = Column(Integer, default=0)  # Para ordenar patrones (mayor prioridad = se evalúa primero)
    is_case_sensitive = Column(Boolean, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    auto_apply = Column(Boolean, default=True)  # Si se aplica automáticamente o solo como sugerencia
    notes = Column(Text)  # Notas adicionales del usuario
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relaciones
    user = relationship("User", back_populates="description_patterns")
    subcategory = relationship("Subcategory")


class PatternMatch(Base):
    """
    Registro de aplicaciones de patrones para auditoría y mejora
    """
    __tablename__ = 'pattern_matches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    pattern_id = Column(Integer, ForeignKey('description_patterns.id'), nullable=False)
    matched_text = Column(String)  # El texto que hizo match
    applied_at = Column(DateTime)
    was_manual_override = Column(Boolean, default=False)  # Si el usuario cambió la categoría después

    # Relaciones
    transaction = relationship("Transaction")
    pattern = relationship("DescriptionPattern")
