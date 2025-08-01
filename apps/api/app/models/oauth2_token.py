from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class OAuth2Token(Base):
    __tablename__ = 'oauth2_tokens'
    __table_args__ = {'schema': 'app'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    provider = Column(String, nullable=False)  # google, facebook, github, etc.
    expires_at = Column(DateTime, nullable=False)
    token_type = Column(String, default='bearer')
    scope = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="oauth_tokens")
    
    @property
    def is_expired(self):
        return datetime.now() > self.expires_at
