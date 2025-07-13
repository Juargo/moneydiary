from sqlalchemy.exc import SQLAlchemyError
from .database import engine, Base
from .config import settings

def initialize_database():
    """Initialize database tables in development mode"""
    if settings.ENVIRONMENT != "production":
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
        except SQLAlchemyError as e:
            print(f"Error creating database tables: {e}")
            raise
