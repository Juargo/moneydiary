from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from .base import Base
from .user_financial_methods import user_financial_methods  

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
    
class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: int
    
    class Config:
        orm_mode = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: int
    permissions: List[PermissionResponse] = []
    
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: Optional[bool] = True
    email_verified: Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    role: Optional[RoleResponse] = None
    
    # Incluir permisos del usuario
    @property
    def permissions(self) -> List[PermissionResponse]:
        # Este campo será computado automáticamente a partir de la propiedad
        # permissions del modelo User
        pass
    
    class Config:
        orm_mode = True
        # Importante: incluir permitir la computación de atributos desde las propiedades del modelo
        computed = ["permissions"]