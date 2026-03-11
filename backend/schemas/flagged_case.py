from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from core.constants import CaseStatus, RiskLevel, FlagType

class FlaggedCaseListItem(BaseModel):
    id: str
    transaction_type: str
    transaction_ref_id: str
    vendor_id: Optional[str]
    flag_type: FlagType
    risk_score: int
    risk_level: RiskLevel
    reason_summary: str
    status: CaseStatus
    created_at: datetime
    
    class Config:
        orm_mode = True

class FlaggedCaseListResponse(BaseModel):
    cases: List[FlaggedCaseListItem]
    total: int
    page: int
    limit: int

class FlaggedCaseDetailResponse(BaseModel):
    id: str
    transaction_type: str
    transaction_ref_id: str
    vendor_id: Optional[str]
    flag_type: FlagType
    risk_score: int
    risk_level: RiskLevel
    reason_summary: str
    status: CaseStatus
    transaction_amount: Optional[Decimal]
    transaction_date: Optional[date]
    department: Optional[str]
    approver: Optional[str]
    explanation: Optional[str]
    recommendation: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True