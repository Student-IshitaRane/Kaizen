from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from app.database.models import RiskLevel, CaseStatus, TransactionType

class FlagInfo(BaseModel):
    type: str
    severity: str
    description: str
    evidence: Optional[Dict[str, Any]] = None

class CaseListItem(BaseModel):
    case_id: str
    case_number: str
    transaction_id: str
    vendor_name: Optional[str]
    amount: Decimal
    risk_score: int
    risk_level: RiskLevel
    flags: List[str]
    status: CaseStatus
    flagged_at: datetime
    
    class Config:
        from_attributes = True

class CaseListResponse(BaseModel):
    cases: List[CaseListItem]
    total: int
    page: int
    limit: int

class TransactionDetail(BaseModel):
    transaction_id: str
    vendor_id: Optional[str]
    vendor_name: Optional[str]
    amount: Decimal
    currency: str
    transaction_date: date
    description: Optional[str]
    department: Optional[str]
    reference_number: Optional[str]

class CaseDetailResponse(BaseModel):
    case_id: str
    case_number: str
    transaction: TransactionDetail
    risk_score: int
    risk_level: RiskLevel
    flags: List[FlagInfo]
    explanation: Optional[str]
    recommendation: Optional[str]
    status: CaseStatus
    assigned_to: Optional[str]
    flagged_at: datetime
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    
    class Config:
        from_attributes = True

class CaseReviewRequest(BaseModel):
    status: CaseStatus
    notes: Optional[str] = None
    action_taken: Optional[str] = None

class CaseReviewResponse(BaseModel):
    case_id: str
    status: CaseStatus
    reviewed_by: str
    reviewed_at: datetime
    
    class Config:
        from_attributes = True

class CaseAssignRequest(BaseModel):
    auditor_id: str

class CaseAssignResponse(BaseModel):
    case_id: str
    assigned_to: str
    assigned_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisScoringBreakdown(BaseModel):
    anomaly_scores: List[Dict[str, Any]]
    pattern_scores: List[Dict[str, Any]]
    validation_scores: List[Dict[str, Any]]
    category_totals: Dict[str, int]
    detailed_scores: Dict[str, Dict[str, Any]]

class SuggestedAction(BaseModel):
    action: str
    rationale: str
    priority: str
    expected_outcome: str

class CaseAnalysisDetailResponse(BaseModel):
    case_id: str
    case_number: str
    transaction: TransactionDetail
    risk_score: int
    risk_level: RiskLevel
    flag_type: str
    reason_summary: str
    detailed_explanation: str
    suggested_actions: List[SuggestedAction]
    scoring_breakdown: AnalysisScoringBreakdown
    analysis_metadata: Dict[str, Any]
    status: CaseStatus
    priority: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    review_notes: Optional[str]
    resolution: Optional[str]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True
