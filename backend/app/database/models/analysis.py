from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database.session import Base

class AnalysisType(str, enum.Enum):
    HISTORICAL = "historical"
    REALTIME = "realtime"
    SCHEDULED = "scheduled"

class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_type = Column(Enum(AnalysisType), nullable=False, index=True)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.QUEUED, index=True)
    progress = Column(Integer, default=0)
    transactions_analyzed = Column(Integer)
    transactions_flagged = Column(Integer)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    triggered_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    error_message = Column(Text)
    analysis_metadata = Column(JSONB)
    
    trigger_user = relationship("User", foreign_keys=[triggered_by])

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_run_id = Column(UUID(as_uuid=True), ForeignKey('analysis_runs.id', ondelete='CASCADE'), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    agent_type = Column(String(100), nullable=False)
    status = Column(String(50), default='pending')
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    execution_time_ms = Column(Integer)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    error_message = Column(Text)
    llm_provider = Column(String(50))
    llm_tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    analysis_run = relationship("AnalysisRun", foreign_keys=[analysis_run_id])
