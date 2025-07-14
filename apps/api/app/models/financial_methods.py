from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Boolean, Date, TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base
from .user_financial_methods import user_financial_methods

class FinancialMethod(Base):
    __tablename__ = 'financial_methods'
    __table_args__ = {'schema': 'app'}
    
    """Modelo para representar métodos financieros en el sistema.
       Un método financiero puede ser utilizado por múltiples usuarios y puede
       estar asociado a diferentes simulaciones financieras y planes de presupuesto."""

    id = Column(Integer, primary_key=True, autoincrement=True) # ID del método financiero
    name = Column(String, nullable=False) # Nombre del método financiero
    description = Column(Text) # Descripción del método financiero
    key = Column(String, nullable=False, unique=True) # Clave única del método financiero
    created_at = Column(TIMESTAMP) # Fecha de creación del método financiero
    updated_at = Column(TIMESTAMP) # Fecha de última actualización del método financiero

    # ============================
    # Relationships and Foreign Keys
    # ============================
    users = relationship(
        "User",
        secondary=user_financial_methods, 
        back_populates="financial_methods"
    ) # Relación muchos a muchos con usuarios a través de la tabla intermedia user_financial_methods
    financial_simulations = relationship("FinancialSimulation", back_populates="financial_method") # Relación con simulaciones financieras asociadas al método financiero
    # Relación con planes de presupuesto asociados al método financiero
    budget_plans = relationship("BudgetPlan", back_populates="financial_method")
    
    # Relaciones con configuraciones específicas de métodos
    method_fifty_thirty_twenty_configs = relationship("MethodFiftyThirtyTwenty", back_populates="financial_method")
    method_envelope_configs = relationship("MethodEnvelope", back_populates="financial_method")
    method_zero_based_configs = relationship("MethodZeroBased", back_populates="financial_method")
    method_kakebo_configs = relationship("MethodKakebo", back_populates="financial_method")
    method_pay_yourself_first_configs = relationship("MethodPayYourselfFirst", back_populates="financial_method")

class MethodFiftyThirtyTwenty(Base):
    __tablename__ = 'method_fifty_thirty_twenty'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False)
    needs_percentage = Column(Numeric, nullable=False, default=50)
    wants_percentage = Column(Numeric, nullable=False, default=30)
    savings_percentage = Column(Numeric, nullable=False, default=20)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_fifty_thirty_twenty")
    financial_method = relationship("FinancialMethod")

class MethodEnvelope(Base):
    __tablename__ = 'method_envelope'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False)
    is_physical = Column(Boolean, nullable=False, default=False)
    rollover_unused = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_envelope")
    financial_method = relationship("FinancialMethod")
    envelopes = relationship("Envelope", back_populates="method_envelope")

class MethodZeroBased(Base):
    __tablename__ = 'method_zero_based'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False)
    include_investments = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_zero_based")
    financial_method = relationship("FinancialMethod")

class MethodKakebo(Base):
    __tablename__ = 'method_kakebo'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False)
    monthly_saving_goal = Column(Numeric, nullable=False, default=0)
    use_weekly_reflection = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_kakebo")
    financial_method = relationship("FinancialMethod")

class MethodPayYourselfFirst(Base):
    __tablename__ = 'method_pay_yourself_first'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False)
    saving_percentage = Column(Numeric, nullable=False, default=20)
    investment_percentage = Column(Numeric, nullable=False, default=10)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="method_pay_yourself_first")
    financial_method = relationship("FinancialMethod")