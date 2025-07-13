from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from .role import roles_permissions
from datetime import datetime

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    resource = Column(String, nullable=False)  # accounts, transactions, etc.
    action = Column(String, nullable=False)    # create, read, update, delete
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    roles = relationship("Role", secondary=roles_permissions, back_populates="permissions")