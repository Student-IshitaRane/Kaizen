from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from core.constants import CaseStatus

class ReviewActionRequest(BaseModel):
    decision: CaseStatus
    comments: Optional[str] = None
    action_taken: Optional[str] = None
    evidence_reviewed: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None

class ReviewActionResponse(BaseModel):
    id: str
    case_id: str
    auditor_id: str
    decision: CaseStatus
    comments: Optional[str]
    reviewed_at: datetime
    
    class Config:
        orm_mode = True