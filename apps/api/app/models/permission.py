from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.role import roles_permissions
import datetime

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    resource = Column(String, nullable=False)  # accounts, transactions, etc.
    action = Column(String, nullable=False)    # create, read, update, delete
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    roles = relationship("Role", secondary=roles_permissions, back_populates="permissions")