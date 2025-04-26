from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from apps.api.app.models.base import Base

class Envelope(Base):
    __tablename__ = 'envelopes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    name = Column(String, nullable=False)
    budget_amount = Column(Numeric, nullable=False, default=0)
    current_balance = Column(Numeric, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="envelopes")
    category = relationship("Category", back_populates="envelopes")
    transactions = relationship("Transaction", back_populates="envelope")
