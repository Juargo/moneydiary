from sqlalchemy import Column, Integer, String, Decimal, ForeignKey, Date, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from apps.api.app.database import Base

class FinancialGoal(Base):
    __tablename__ = 'financial_goals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Decimal, nullable=False)
    current_amount = Column(Decimal, nullable=False, default=0)
    start_date = Column(Date, nullable=False)
    target_date = Column(Date)
    category_id = Column(Integer, ForeignKey('categories.id'))
    is_completed = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="financial_goals")
    category = relationship("Category", back_populates="financial_goals")

class GoalContribution(Base):
    __tablename__ = 'goal_contributions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey('financial_goals.id'), nullable=False)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    amount = Column(Decimal, nullable=False)
    contribution_date = Column(Date, nullable=False)
    notes = Column(Text)

    goal = relationship("FinancialGoal", back_populates="contributions")
    transaction = relationship("Transaction", back_populates="goal_contributions")