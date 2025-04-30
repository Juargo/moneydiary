from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Boolean, Date, TIMESTAMP
from sqlalchemy.orm import relationship
from apps.api.app.models.base import Base

class FinancialMethod(Base):
    __tablename__ = 'financial_methods'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    key = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    users = relationship(
        "User",
        secondary="user_financial_methods",  # tabla de unión
        back_populates="financial_methods"
    )

class MethodFiftyThirtyTwenty(Base):
    __tablename__ = 'method_fifty_thirty_twenty'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    needs_percentage = Column(Numeric, nullable=False, default=50)
    wants_percentage = Column(Numeric, nullable=False, default=30)
    savings_percentage = Column(Numeric, nullable=False, default=20)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_fifty_thirty_twenty")

class MethodEnvelope(Base):
    __tablename__ = 'method_envelope'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_physical = Column(Boolean, nullable=False, default=False)
    rollover_unused = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_envelope")

class MethodZeroBased(Base):
    __tablename__ = 'method_zero_based'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    include_investments = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_zero_based")

class MethodKakebo(Base):
    __tablename__ = 'method_kakebo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    monthly_saving_goal = Column(Numeric, nullable=False, default=0)
    use_weekly_reflection = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_kakebo")

class MethodPayYourselfFirst(Base):
    __tablename__ = 'method_pay_yourself_first'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    saving_percentage = Column(Numeric, nullable=False, default=20)
    investment_percentage = Column(Numeric, nullable=False, default=10)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_pay_yourself_first")