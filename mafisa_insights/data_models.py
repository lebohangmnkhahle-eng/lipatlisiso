from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Financials:
    monthly_revenue: float
    monthly_expenses: float
    inventory_value: float
    transaction_frequency: int  # e.g., transactions per month
    payment_methods: List[str] = field(default_factory=list)  # e.g., ["Cash", "Mobile Money", "Bank Transfer"]

@dataclass
class MSME:
    id: str
    name: str
    sector: str
    location: str
    years_in_business: int
    employee_count: int
    contact_info: str
    financials: Financials
    credit_score: Optional[int] = None
    risk_category: Optional[str] = None
