from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
import datetime

class OAuth2Token(Base):
    __tablename__ = 'oauth2_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    provider = Column(String, nullable=False)  # google, facebook, github, etc.
    expires_at = Column(DateTime, nullable=False)
    token_type = Column(String, default='bearer')
    scope = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="oauth_tokens")
    
    @property
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_at