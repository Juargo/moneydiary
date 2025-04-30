from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from apps.api.app.models.base import Base

class FinancialGoal(Base):
    __tablename__ = 'financial_goals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Numeric, nullable=False)
    current_amount = Column(Numeric, nullable=False, default=0)
    start_date = Column(Date, nullable=False)
    target_date = Column(Date)
    category_id = Column(Integer, ForeignKey('categories.id'))
    is_completed = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="financial_goals")
    category = relationship("Category", back_populates="financial_goals")
    contributions = relationship("GoalContribution", back_populates="goal")

class GoalContribution(Base):
    __tablename__ = 'goal_contributions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey('financial_goals.id'), nullable=False)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    amount = Column(Numeric, nullable=False)
    contribution_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    goal = relationship("FinancialGoal", back_populates="contributions")
    transaction = relationship("Transaction", back_populates="goal_contributions")