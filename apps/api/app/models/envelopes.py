from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Envelope(Base):
    __tablename__ = 'envelopes'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    method_envelope_id = Column(Integer, ForeignKey('method_envelope.id'), nullable=False)
    name = Column(String, nullable=False)
    budget_amount = Column(Numeric, nullable=False, default=0)
    current_balance = Column(Numeric, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="envelopes")
    category = relationship("Category", back_populates="envelopes")
    method_envelope = relationship("MethodEnvelope", back_populates="envelopes")
    transactions = relationship("Transaction", back_populates="envelope")
    budget_items = relationship("BudgetItem", back_populates="envelope")
