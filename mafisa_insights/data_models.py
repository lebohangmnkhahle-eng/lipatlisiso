from dataclasses import dataclass, field
from typing import List, Optional, Dict

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

@dataclass
class DirectoryListing:
    name: str
    sector: str
    location: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    social_links: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None
    source_url: str = ""
    scraped_at: str = ""
