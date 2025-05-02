from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .base import Base

class CategoryGroup(Base):
    __tablename__ = 'category_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_expense = Column(Boolean, nullable=False)
    icon = Column(String)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_group_id = Column(Integer, ForeignKey('category_groups.id'))
    name = Column(String, nullable=False)
    is_income = Column(Boolean, nullable=False)
    icon = Column(String)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    category_group = relationship("CategoryGroup", back_populates="categories")

class Subcategory(Base):
    __tablename__ = 'subcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    name = Column(String, nullable=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    category = relationship("Category", back_populates="subcategories")

CategoryGroup.categories = relationship("Category", order_by=Category.id, back_populates="category_group")
Category.subcategories = relationship("Subcategory", order_by=Subcategory.id, back_populates="category")