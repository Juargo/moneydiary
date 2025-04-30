from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from apps.api.app.models.base import Base

class BudgetPlan(Base):
    __tablename__ = 'budget_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False)
    name = Column(String, nullable=False)
    total_income = Column(Numeric, nullable=False, default=0)
    total_expenses = Column(Numeric, nullable=False, default=0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="budget_plans")
    financial_method = relationship("FinancialMethod", back_populates="budget_plans")
    budget_items = relationship("BudgetItem", back_populates="budget_plan")


class BudgetItem(Base):
    __tablename__ = 'budget_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(Integer, ForeignKey('budget_plans.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'))
    envelope_id = Column(Integer, ForeignKey('envelopes.id'))
    amount = Column(Numeric, nullable=False)
    month_year = Column(String, nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    budget_plan = relationship("BudgetPlan", back_populates="budget_items")
    category = relationship("Category", back_populates="budget_items")
    subcategory = relationship("Subcategory", back_populates="budget_items")
    envelope = relationship("Envelope", back_populates="budget_items")
