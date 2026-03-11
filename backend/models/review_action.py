from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base
from core.constants import CaseStatus

class ReviewAction(Base):
    __tablename__ = "review_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey('flagged_cases.id'), nullable=False, index=True)
    auditor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    decision = Column(Enum(CaseStatus), nullable=False)
    comments = Column(String(2000))
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional fields for audit trail
    action_taken = Column(String(1000))
    evidence_reviewed = Column(String(2000))
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    
    case = relationship("FlaggedCase", foreign_keys=[case_id])
    auditor = relationship("User", foreign_keys=[auditor_id])