from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base

class BudgetPlan(Base):
    __tablename__ = 'budget_plans'
    __table_args__ = {'schema': 'app'}
    
    """
    Modelo para representar planes de presupuesto en el sistema.
    Un plan de presupuesto puede contener múltiples partidas presupuestarias y está asociado a un usuario y
    un método financiero específico.
    """

    id = Column(Integer, primary_key=True, autoincrement=True) # ID del plan de presupuesto
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # ID del usuario propietario del plan de presupuesto
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False) # ID del método financiero asociado al plan de presupuesto
    name = Column(String, nullable=False) # Nombre del plan de presupuesto
    total_income = Column(Numeric, nullable=False, default=0) # Ingresos totales del plan de presupuesto
    total_expenses = Column(Numeric, nullable=False, default=0) # Gastos totales del plan de presupuesto
    start_date = Column(Date, nullable=False) # Fecha de inicio del plan de presupuesto
    end_date = Column(Date, nullable=False) # Fecha de finalización del plan de presupuesto
    is_active = Column(Boolean, default=True) # Indica si el plan de presupuesto está activo
    created_at = Column(TIMESTAMP) # Fecha de creación del plan de presupuesto
    updated_at = Column(TIMESTAMP) # Fecha de última actualización del plan de presupuesto

    # ============================
    # Relationships and Foreign Keys
    # ============================
    user = relationship("User", back_populates="budget_plans") # Relación con el modelo User
    financial_method = relationship("FinancialMethod", back_populates="budget_plans") # Relación con el modelo FinancialMethod
    budget_items = relationship("BudgetItem", back_populates="budget_plan") # Partidas presupuestarias asociadas al plan de presupuesto

    # EJEMPLO EN descripción narrativa del modelo entidad-relación:
    # Un plan de presupuesto (BudgetPlan) puede tener múltiples partidas presupuestarias (BudgetItem), cada una asociada a una categoría y subcategoría específica.
    # Cada partida presupuestaria (BudgetItem) puede tener un monto específico asignado para un mes y año determinados.
    # Las partidas presupuestarias pueden estar asociadas a sobres (envelopes) para un mejor control del gasto.

class BudgetItem(Base):
    __tablename__ = 'budget_items'
    __table_args__ = {'schema': 'app'}
    """Modelo para representar partidas presupuestarias dentro de un plan de presupuesto.
    Cada partida presupuestaria está asociada a una categoría, subcategoría y sobres (envelopes) específicos.
    Permite definir montos específicos para cada partida en un mes y año determinados."""

    id = Column(Integer, primary_key=True, autoincrement=True) # ID de la partida presupuestaria
    budget_id = Column(Integer, ForeignKey('budget_plans.id'), nullable=False) # ID del plan de presupuesto al que pertenece la partida
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False) # ID de la subcategoría asociada a la partida presupuestaria
    envelope_id = Column(Integer, ForeignKey('envelopes.id')) # ID del sobre (envelope) asociado a la partida presupuestaria
    amount = Column(Numeric, nullable=False) # Monto de la partida presupuestaria
    month_year = Column(String, nullable=False) # Mes y año de la partida presupuestaria
    notes = Column(Text) # Notas adicionales sobre la partida presupuestaria
    created_at = Column(TIMESTAMP) # Fecha de creación de la partida presupuestaria
    updated_at = Column(TIMESTAMP) # Fecha de última actualización de la partida presupuestaria

    # ============================
    # Relationships and Foreign Keys
    # ============================
    budget_plan = relationship("BudgetPlan", back_populates="budget_items") # Relación con el modelo BudgetPlan
    subcategory = relationship("Subcategory", back_populates="budget_items") # Relación con el modelo Subcategory
    envelope = relationship("Envelope", back_populates="budget_items") # Relación con el modelo Envelope
    
    # Propiedad para acceder a la categoría a través de la subcategoría
    @property
    def category(self):
        return self.subcategory.category if self.subcategory else None
