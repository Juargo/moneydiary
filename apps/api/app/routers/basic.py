from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db
from ..config import settings
from ..lifecycle import VERSION
from ..db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER

# Create router
router = APIRouter(tags=["basic"])

@router.get("/")
async def root():
    return {
        "message": f"MoneyDiary API v{VERSION}",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "graphql_endpoint": "/graphql",
        "api_endpoint": "/api"
    }

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = {
            "error": str(e),
            "connection_url": f"postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME,
            "user": DB_USER
        }
    
    return {
        "status": "ok" if db_status == "ok" else "error",
        "version": VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }
