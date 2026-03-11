from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, CheckConstraint, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base
from core.constants import CaseStatus, RiskLevel, FlagType

class FlaggedCase(Base):
    __tablename__ = "flagged_cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_type = Column(String(50), nullable=False, index=True)
    transaction_ref_id = Column(String(100), nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.id'), nullable=True, index=True)
    flag_type = Column(Enum(FlagType), nullable=False, index=True)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False, index=True)
    reason_summary = Column(String(1000))
    status = Column(Enum(CaseStatus), default=CaseStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Additional fields for audit analytics
    transaction_amount = Column(Numeric(15, 2))
    transaction_date = Column(Date)
    department = Column(String(100))
    approver = Column(String(255))
    explanation = Column(String(2000))
    recommendation = Column(String(1000))
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(String(2000))
    action_taken = Column(String(1000))
    resolved_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        CheckConstraint('risk_score >= 0 AND risk_score <= 100', name='check_risk_score_range'),
    )
    
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    reviewer = relationship("User", foreign_keys=[reviewed_by])