from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from apps.api.app.models.base import Base

class AccountType(Base):
    __tablename__ = 'account_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    accounts = relationship("Account", back_populates="account_type")
