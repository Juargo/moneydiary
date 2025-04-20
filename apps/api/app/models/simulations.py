from sqlalchemy import Column, Integer, String, Text, Date, Decimal, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from apps.api.app.database import Base

class FinancialSimulation(Base):
    __tablename__ = 'financial_simulations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    financial_method_id = Column(Integer, ForeignKey('financial_methods.id'), nullable=False)
    base_income = Column(Decimal, nullable=False)
    start_date = Column(Date, nullable=False)
    months_duration = Column(Integer, nullable=False, default=12)

    user = relationship("User", back_populates="financial_simulations")
    financial_method = relationship("FinancialMethod", back_populates="financial_simulations")
    scenarios = relationship("SimulationScenario", back_populates="financial_simulation")

class SimulationScenario(Base):
    __tablename__ = 'simulation_scenarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(Integer, ForeignKey('financial_simulations.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_baseline = Column(Boolean, nullable=False, default=False)

    financial_simulation = relationship("FinancialSimulation", back_populates="scenarios")
    parameters = relationship("SimulationParameter", back_populates="scenario")
    results = relationship("SimulationResult", back_populates="scenario")

class SimulationParameter(Base):
    __tablename__ = 'simulation_parameters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey('simulation_scenarios.id'), nullable=False)
    parameter_key = Column(String, nullable=False)
    parameter_value = Column(String, nullable=False)

    scenario = relationship("SimulationScenario", back_populates="parameters")

class SimulationResult(Base):
    __tablename__ = 'simulation_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(Integer, ForeignKey('simulation_scenarios.id'), nullable=False)
    month_year = Column(String, nullable=False)
    income_total = Column(Decimal, nullable=False)
    expense_total = Column(Decimal, nullable=False)
    monthly_savings = Column(Decimal, nullable=False)
    accumulated_savings = Column(Decimal, nullable=False)
    net_worth = Column(Decimal, nullable=False)

    scenario = relationship("SimulationScenario", back_populates="results")