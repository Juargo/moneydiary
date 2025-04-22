from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import engine, get_db, Base, DB_HOST, DB_PORT, DB_NAME, DB_USER
from .config import settings

# Version definition
VERSION = "0.1.0"

# Create app
app = FastAPI(
    title="MoneyDiary API",
    description="API for the MoneyDiary app",
    version=VERSION
)

# Import all models to ensure they're registered with SQLAlchemy
# Import models in dependency order
from .models.financial_methods import (
    FinancialMethod, MethodFiftyThirtyTwenty, MethodEnvelope,
    MethodZeroBased, MethodKakebo, MethodPayYourselfFirst
)
from .models.account_types import AccountType
from .models.categories import CategoryGroup, Category, Subcategory
from .models.users import User
from .models.accounts import Account
from .models.envelopes import Envelope
from .models.recurring_patterns import RecurringPattern
from .models.csv_imports import CsvImport, CsvImportProfile, CsvColumnMapping, ImportError
from .models.transactions import TransactionStatus, Transaction
from .models.budget import BudgetPlan, BudgetItem
from .models.financial_goals import FinancialGoal, GoalContribution
from .models.projections import ProjectionSettings, MonthlyProjections, ProjectionDetails
from .models.simulations import (
    FinancialSimulation, SimulationScenario,
    SimulationParameter, SimulationResult
)

# Create tables in development mode (for production, use Alembic)
if settings.ENVIRONMENT != "production":
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {e}")
        raise

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {
        "message": f"MoneyDiary API v{VERSION}",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "graphql_endpoint": "/graphql",
        "api_endpoint": "/api"
    }

@app.get("/health")
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

# Include routes (commented out until implemented)
# app.include_router(api_router, prefix="/api")
