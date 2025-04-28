from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, Numeric, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from app.models.base import Base

class TransactionStatus(Base):
    __tablename__ = 'transaction_statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    transfer_account_id = Column(Integer, ForeignKey('accounts.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'))
    envelope_id = Column(Integer, ForeignKey('envelopes.id'))
    status_id = Column(Integer, ForeignKey('transaction_statuses.id'), nullable=False)
    recurring_pattern_id = Column(Integer, ForeignKey('recurring_patterns.id'))
    import_id = Column(Integer, ForeignKey('csv_imports.id'))
    external_id = Column(String)
    amount = Column(Numeric, nullable=False)
    description = Column(Text)
    notes = Column(Text)
    transaction_date = Column(Date, nullable=False)
    is_recurring = Column(Boolean, nullable=False, default=False)
    is_planned = Column(Boolean, nullable=False, default=False)
    kakebo_emotion = Column(String)

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    transfer_account = relationship("Account", foreign_keys=[transfer_account_id])
    category = relationship("Category", back_populates="transactions")
    subcategory = relationship("Subcategory", back_populates="transactions")
    envelope = relationship("Envelope", back_populates="transactions")
    status = relationship("TransactionStatus", back_populates="transactions")
    recurring_pattern = relationship("RecurringPattern", back_populates="transactions")
    import_data = relationship("CSVImport", back_populates="transactions")