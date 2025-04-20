import strawberry
from typing import Optional, List
from datetime import datetime

@strawberry.type
class FinancialMethodType:
    id: int
    name: str
    description: Optional[str]
    key: str
    created_at: datetime
    updated_at: datetime
    
    # Métodos específicos se implementarían como types adicionales
    # fifty_thirty_twenty_config: Optional["MethodFiftyThirtyTwentyType"]
    # envelope_config: Optional["MethodEnvelopeType"]
    # etc.

@strawberry.type
class MethodFiftyThirtyTwentyType:
    id: int
    user_id: int
    needs_percentage: float
    wants_percentage: float
    savings_percentage: float
    created_at: datetime
    updated_at: datetime

# Tipos similares para otros métodos financieros