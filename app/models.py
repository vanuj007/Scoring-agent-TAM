from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CompanyType(str, Enum):
    startup = "Startup"
    scale_up = "Scale-up"
    pe_backed_growth = "PE-backed growth company"
    public_tech = "Public tech company"
    traditional_enterprise = "Traditional enterprise"


class FundingStatus(str, Enum):
    vc_backed = "VC-backed"
    bootstrapped = "Bootstrapped"
    pe_backed = "PE-backed"
    public = "Public"
    unknown = "Unknown"


class RevenueBand(str, Enum):
    band_1m_100m = "$1M-$100M"
    under_1m = "<$1M"
    over_100m = ">$100M"
    unknown = "Unknown"


class Geography(str, Enum):
    global_remote = "Global/remote hiring"
    us = "US"
    europe = "Europe"
    india = "India"
    sea_middle_east = "SEA/Middle East"
    other = "Other"


class TamScoreRequest(BaseModel):
    company_type: CompanyType
    employee_count: int = Field(..., ge=0)
    funding_status: FundingStatus
    revenue_band: Optional[RevenueBand] = None
    geography: Geography


class TamScoreResponse(BaseModel):
    tam_score: int
    tam_decision: str
    tam_category: str
    reason_codes: list[str]


class FreeTextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Free-text description of the company")


class FreeTextExtraction(TamScoreRequest):
    pass
