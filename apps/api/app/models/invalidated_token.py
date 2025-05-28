from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class InvalidatedToken(Base):
    __tablename__ = 'invalidated_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String, unique=True, nullable=False)  # JWT ID único
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, default=datetime.datetime.now)
    
    user = relationship("User", back_populates="invalidated_tokens")
    
    @property
    def is_expired(self):
        return datetime.datetime.now() > self.expires_at