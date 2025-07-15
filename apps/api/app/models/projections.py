from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base

class ProjectionSettings(Base):
    __tablename__ = 'projection_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    initial_balance = Column(Numeric, nullable=False, default=0)
    inflation_rate = Column(Numeric, nullable=False, default=0.03)
    income_growth_rate = Column(Numeric, nullable=False, default=0.03)
    projection_months = Column(Integer, nullable=False, default=36)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="projections")

class MonthlyProjections(Base):
    __tablename__ = 'monthly_projections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    month_year = Column(String, nullable=False)
    initial_balance = Column(Numeric, nullable=False)
    income_total = Column(Numeric, nullable=False)
    expense_total = Column(Numeric, nullable=False)
    monthly_balance = Column(Numeric, nullable=False)
    end_balance = Column(Numeric, nullable=False)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'))
    is_simulation = Column(Boolean, nullable=False, default=False)
    simulation_name = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="monthly_projections")
    financial_method = relationship("FinancialMethod")
    projection_details = relationship("ProjectionDetails", back_populates="projection")

class ProjectionDetails(Base):
    __tablename__ = 'projection_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    projection_id = Column(Integer, ForeignKey('monthly_projections.id'), nullable=False)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False)
    amount = Column(Numeric, nullable=False)
    is_actual = Column(Boolean, nullable=False, default=False)
    financial_bucket = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    projection = relationship("MonthlyProjections", back_populates="projection_details")
    subcategory = relationship("Subcategory")