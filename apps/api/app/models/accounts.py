from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from .base import Base

class Account(Base):
    __tablename__ = 'accounts'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True) # ID de la cuenta
    name = Column(String(100), nullable=False) # Nombre de la cuenta
    account_number = Column(String(50), nullable=True)  # Número de cuenta
    current_balance = Column(Float, default=0.0) # Saldo actual de la cuenta
    active = Column(Boolean, default=True) # Indica si la cuenta está activa
    created_at = Column(DateTime, default=func.now()) # Fecha de creación de la cuenta
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) # Fecha de última actualización de la cuenta

    # ============================
    # Relationships and Foreign Keys
    # ============================
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # ID del usuario propietario de la cuenta
    bank_id = Column(Integer, ForeignKey("banks.id"), nullable=False) # ID del banco asociado a la cuenta
    account_type_id = Column(Integer, ForeignKey("account_types.id"), nullable=False) # ID del tipo de cuenta

    user = relationship("User", back_populates="accounts") # Relación con el modelo User
    bank = relationship("Bank", back_populates="accounts") # Relación con el modelo Bank
    account_type = relationship("AccountType", back_populates="accounts") # Relación con el modelo AccountType
    transactions = relationship("Transaction", back_populates="account", foreign_keys="Transaction.account_id") # Relación con las transacciones asociadas a la cuenta
    incoming_transfers = relationship("Transaction", back_populates="transfer_account", foreign_keys="Transaction.transfer_account_id") # Relación con las transferencias entrantes asociadas a la cuenta


    # ============================

    # is_tracking_only = Column(Boolean, nullable=False, default=False)
    # include_in_net_worth = Column(Boolean, nullable=False, default=True)
