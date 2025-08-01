from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, Numeric, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base

class TransactionStatus(Base):
    __tablename__ = 'transaction_statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    transactions = relationship("Transaction", back_populates="status")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    transfer_account_id = Column(Integer, ForeignKey('accounts.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'))
    envelope_id = Column(Integer, ForeignKey('envelopes.id'))
    status_id = Column(Integer, ForeignKey('transaction_statuses.id'), nullable=False)
    recurring_pattern_id = Column(Integer, ForeignKey('recurring_patterns.id'))
    import_id = Column(Integer, ForeignKey('file_imports.id'))
    import_row_number = Column(Integer, nullable=True)
    external_id = Column(String)
    amount = Column(Numeric, nullable=False)
    description = Column(Text)
    notes = Column(Text)
    transaction_date = Column(Date, nullable=False)
    is_recurring = Column(Boolean, nullable=False, default=False)
    is_planned = Column(Boolean, nullable=False, default=False)
    kakebo_emotion = Column(String)

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", 
                          back_populates="transactions", 
                          foreign_keys=[account_id])    
    transfer_account = relationship("Account", 
                                  back_populates="incoming_transfers", 
                                  foreign_keys=[transfer_account_id])
    subcategory = relationship("Subcategory", back_populates="transactions")
    envelope = relationship("Envelope", back_populates="transactions")
    status = relationship("TransactionStatus", back_populates="transactions")
    recurring_pattern = relationship("RecurringPattern", back_populates="transactions")
    import_data = relationship("FileImport", back_populates="transactions")
    goal_contributions = relationship("GoalContribution", back_populates="transaction")
