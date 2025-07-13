from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, TIMESTAMP, Boolean, Text
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
