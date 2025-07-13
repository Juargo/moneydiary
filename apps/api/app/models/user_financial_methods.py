from sqlalchemy import Table, Column, ForeignKey, Integer
from .base import Base

# Define the association table for User and FinancialMethod
user_financial_methods = Table(
    'user_financial_methods',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('financial_method_id', Integer, ForeignKey('financial_methods.id'), primary_key=True)
)