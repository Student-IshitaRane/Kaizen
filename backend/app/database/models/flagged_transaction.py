from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database.session import Base

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CaseStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED_SUSPICIOUS = "confirmed_suspicious"
    FALSE_POSITIVE = "false_positive"
    NEEDS_REVIEW = "needs_review"
    RESOLVED = "resolved"

class FlaggedTransaction(Base):
    __tablename__ = "flagged_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False, index=True)
    analysis_run_id = Column(UUID(as_uuid=True), ForeignKey('analysis_runs.id', ondelete='SET NULL'))
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False, index=True)
    flags = Column(JSONB, nullable=False)
    explanation = Column(Text)
    recommendation = Column(Text)
    status = Column(Enum(CaseStatus), default=CaseStatus.PENDING, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), index=True)
    assigned_at = Column(DateTime(timezone=True))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)
    action_taken = Column(Text)
    flagged_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    case_metadata = Column(JSONB)
    
    __table_args__ = (
        CheckConstraint('risk_score >= 0 AND risk_score <= 100', name='check_risk_score_range'),
    )
    
    transaction = relationship("Transaction", foreign_keys=[transaction_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

class FlagDetail(Base):
    __tablename__ = "flag_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flagged_transaction_id = Column(UUID(as_uuid=True), ForeignKey('flagged_transactions.id', ondelete='CASCADE'), nullable=False, index=True)
    flag_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSONB)
    agent_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    flagged_transaction = relationship("FlaggedTransaction", foreign_keys=[flagged_transaction_id])
