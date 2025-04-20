from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from apps.api.app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    default_financial_method_id = Column(Integer, ForeignKey('financial_methods.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    financial_method = relationship("FinancialMethod", back_populates="users")
    accounts = relationship("Account", back_populates="user")
    method_fifty_thirty_twenty = relationship("MethodFiftyThirtyTwenty", uselist=False, back_populates="user")
    method_envelope = relationship("MethodEnvelope", uselist=False, back_populates="user")
    method_zero_based = relationship("MethodZeroBased", uselist=False, back_populates="user")
    method_kakebo = relationship("MethodKakebo", uselist=False, back_populates="user")
    method_pay_yourself_first = relationship("MethodPayYourselfFirst", uselist=False, back_populates="user")
    financial_goals = relationship("FinancialGoal", back_populates="user")
    budget_plans = relationship("BudgetPlan", back_populates="user")
    csv_imports = relationship("CsvImport", back_populates="user")
    projections = relationship("ProjectionSetting", back_populates="user")
    financial_simulations = relationship("FinancialSimulation", back_populates="user")