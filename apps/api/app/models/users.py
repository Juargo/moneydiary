from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

from .base import Base
from .user_financial_methods import user_financial_methods  

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'app'}  

    id = Column(Integer, primary_key=True, autoincrement=True) # ID del usuario
    name = Column(String, nullable=False) # Nombre del usuario
    email = Column(String, unique=True, nullable=False) # Correo electrónico del usuario
    password_hash = Column(String, nullable=False) # Hash de la contraseña del usuario
    default_financial_method_id = Column(Integer, ForeignKey('financial_methods.id')) # Método financiero por defecto del usuario
    created_at = Column(DateTime, default=datetime.now(timezone.utc)) # Fecha de creación del usuario
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)) # Fecha de última actualización del usuario
    profile_image = Column(String, nullable=True) # URL de la imagen de perfil del usuario
    is_active = Column(Boolean, nullable=True) # Indica si el usuario está activo
    email_verified = Column(Boolean, nullable=True) # Indica si el correo electrónico del usuario ha sido verificado
    last_login = Column(DateTime, nullable=True) # Fecha del último inicio de sesión del usuario
    
    # ============================
    # Relaciones y Claves Foráneas
    # ============================
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True) # ID del rol del usuario

    financial_method = relationship("FinancialMethod", back_populates="users") # Relación con el método financiero por defecto
    accounts = relationship("Account", back_populates="user") # Relación con las cuentas del usuario
    method_fifty_thirty_twenty = relationship("MethodFiftyThirtyTwenty", uselist=False, back_populates="user") # Relación con el método 50/30/20
    method_envelope = relationship("MethodEnvelope", uselist=False, back_populates="user") # Relación con el método de sobres
    method_zero_based = relationship("MethodZeroBased", uselist=False, back_populates="user") # Relación con el método de presupuesto base cero
    method_kakebo = relationship("MethodKakebo", uselist=False, back_populates="user") # Relación con el método Kakebo
    method_pay_yourself_first = relationship("MethodPayYourselfFirst", uselist=False, back_populates="user") # Relación con el método "Págate a ti mismo primero"
    financial_goals = relationship("FinancialGoal", back_populates="user") # Relación con los objetivos financieros
    budget_plans = relationship("BudgetPlan", back_populates="user") # Relación con los planes de presupuesto
    file_imports = relationship("FileImport", back_populates="user") # Relación con las importaciones de archivos
    file_import_profiles = relationship("FileImportProfile", back_populates="user")  # Relación con los perfiles de importación de archivos
    projections = relationship("ProjectionSettings", back_populates="user") # Relación con la configuración de proyecciones
    financial_simulations = relationship("FinancialSimulation", back_populates="user") # Relación con las simulaciones financieras
    role_relation = relationship("Role", back_populates="users") # Relación con los roles
    oauth_tokens = relationship("OAuth2Token", back_populates="user", cascade="all, delete-orphan") # Relación con los tokens OAuth2
    invalidated_tokens = relationship("InvalidatedToken", back_populates="user", cascade="all, delete-orphan") # Relación con los tokens invalidados
    monthly_projections = relationship("MonthlyProjections", back_populates="user") # Relación con las proyecciones mensuales
    financial_methods = relationship("FinancialMethod", secondary=user_financial_methods, back_populates="users") # Relación con los métodos financieros
    transactions = relationship("Transaction", back_populates="user") # Relación con las transacciones
    recurring_patterns = relationship("RecurringPattern", back_populates="user") # Relación con los patrones recurrentes
    envelopes = relationship("Envelope", back_populates="user") # Relación con los sobres

    @property
    def permissions(self):
        """Obtiene todos los permisos del usuario a través de su rol"""
        if not self.role_relation:
            return []
        return self.role_relation.permissions
    
class PermissionBase(BaseModel):
    """
    Represents a permission definition for a user.

    Attributes:
        name (str): The name of the permission.
        resource (str): The resource to which the permission applies.
        action (str): The action allowed by the permission (e.g., 'read', 'write').
        description (Optional[str]): An optional description of the permission.
    """
    name: str
    resource: str
    action: str
    description: Optional[str] = None

class PermissionResponse(PermissionBase):
    """
    Represents a response model for user permissions.
    Inherits from:
        PermissionBase: The base model containing common permission fields.
    Attributes:
        id (int): Unique identifier for the permission.
    Config:
        from_attributes (bool): Enables compatibility with ORM objects.
    """
    id: int
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    """
    RoleBase defines the base schema for a user role.

    Attributes:
        name (str): The name of the role.
        description (Optional[str]): An optional description of the role.
    """
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    """
    Represents a response model for a user role, extending RoleBase.
    Attributes:
        id (int): Unique identifier for the role.
        permissions (List[PermissionResponse]): List of permissions associated with the role.
    Config:
        from_attributes (bool): Enables compatibility with ORM objects.
    """
    id: int
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """
    Base model for user data.

    Attributes:
        email (str): The user's email address.
        name (Optional[str]): The user's full name. Defaults to None.
        profile_image (Optional[str]): URL or path to the user's profile image. Defaults to None.
        is_active (Optional[bool]): Indicates if the user account is active. Defaults to True.
        email_verified (Optional[bool]): Indicates if the user's email has been verified. Defaults to False.
    """
    email: str
    name: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: Optional[bool] = True
    email_verified: Optional[bool] = False

class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Inherits from:
        UserBase: Base user schema with common user fields.

    Attributes:
        password (str): The password for the new user account.
    """
    password: str

class UserUpdate(UserBase):
    """
    Data model for updating user information.

    Inherits from:
        UserBase

    Attributes:
        password (Optional[str]): The new password for the user. If not provided, the password will remain unchanged.
    """
    password: Optional[str] = None

class UserResponse(UserBase):
    """
    UserResponse schema for API responses.
    Inherits from:
        UserBase
    Attributes:
        id (int): Unique identifier for the user.
        created_at (Optional[datetime]): Timestamp when the user was created.
        updated_at (Optional[datetime]): Timestamp when the user was last updated.
        role (Optional[RoleResponse]): Role information associated with the user.
    Properties:
        permissions (List[PermissionResponse]): Computed list of permissions derived from the user's role or assignments.
    Config:
        from_attributes (bool): Enables compatibility with ORM objects.
        computed (List[str]): Specifies computed properties to include in serialization (e.g., "permissions").
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    role: Optional[RoleResponse] = None
    
    @property
    def permissions(self) -> List[PermissionResponse]:
        # Este campo será computado automáticamente a partir de la propiedad
        # permissions del modelo User
        if self.role and self.role.permissions:
            return self.role.permissions
        return []
    
    class Config:
        from_attributes = True
        # Importante: incluir permitir la computación de atributos desde las propiedades del modelo
        computed = ["permissions"]