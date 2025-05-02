from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .base import Base
from .user_financial_methods import user_financial_methods  
import datetime

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'app'}  

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    default_financial_method_id = Column(Integer, ForeignKey('financial_methods.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Campos adicionales para OAuth2/JWT
    profile_image = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=True)
    email_verified = Column(Boolean, nullable=True)
    last_login = Column(DateTime, nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)

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
    csv_import_profiles = relationship("CsvImportProfile", back_populates="user")  # Agregar esta línea
    projections = relationship("ProjectionSettings", back_populates="user")
    financial_simulations = relationship("FinancialSimulation", back_populates="user")
    role_relation = relationship("Role", back_populates="users")
    oauth_tokens = relationship("OAuth2Token", back_populates="user", cascade="all, delete-orphan")
    invalidated_tokens = relationship("InvalidatedToken", back_populates="user", cascade="all, delete-orphan")
    monthly_projections = relationship("MonthlyProjections", back_populates="user")
    
    financial_methods = relationship(
        "FinancialMethod",
        secondary=user_financial_methods,  # Now using the imported table object
        back_populates="users"
    )
    transactions = relationship("Transaction", back_populates="user")
    recurring_patterns = relationship("RecurringPattern", back_populates="user")
    envelopes = relationship("Envelope", back_populates="user")

    @property
    def permissions(self):
        """Obtiene todos los permisos del usuario a través de su rol"""
        if not self.role_relation:
            return []
        return self.role_relation.permissions