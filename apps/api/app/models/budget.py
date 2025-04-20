from sqlalchemy import Column, Integer, String, ForeignKey, Decimal, Date, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from apps.api.app.database import Base

class BudgetPlans(Base):
    __tablename__ = 'budget_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("Users", back_populates="budget_plans")
    financial_method = relationship("FinancialMethods", back_populates="budget_plans")
    budget_items = relationship("BudgetItems", back_populates="budget_plan")


class BudgetItems(Base):
    __tablename__ = 'budget_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(Integer, ForeignKey('budget_plans.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'))
    envelope_id = Column(Integer, ForeignKey('envelopes.id'))
    amount = Column(Decimal, nullable=False)
    month_year = Column(String, nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    budget_plan = relationship("BudgetPlans", back_populates="budget_items")
    category = relationship("Categories", back_populates="budget_items")
    subcategory = relationship("Subcategories", back_populates="budget_items")
    envelope = relationship("Envelopes", back_populates="budget_items")