class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_type_id = Column(Integer, ForeignKey('account_types.id'), nullable=False)
    name = Column(String, nullable=False)
    current_balance = Column(Decimal, nullable=False, default=0)
    is_tracking_only = Column(Boolean, nullable=False, default=False)
    include_in_net_worth = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="accounts")
    account_type = relationship("AccountType", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")