from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database.session import Base

class DatasetType(str, enum.Enum):
    VENDOR_MASTER = "vendor_master"
    PURCHASE_LEDGER = "purchase_ledger"
    SALES_LEDGER = "sales_ledger"
    GENERAL_LEDGER = "general_ledger"
    BANK_TRANSACTIONS = "bank_transactions"

class UploadStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Upload(Base):
    __tablename__ = "uploads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    dataset_type = Column(Enum(DatasetType), nullable=False, index=True)
    file_size = Column(Integer)
    file_path = Column(Text)
    status = Column(Enum(UploadStatus), default=UploadStatus.PROCESSING, index=True)
    rows_total = Column(Integer)
    rows_processed = Column(Integer)
    rows_failed = Column(Integer)
    error_log = Column(JSONB)
    description = Column(Text)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    upload_metadata = Column(JSONB)
    
    uploader = relationship("User", foreign_keys=[uploaded_by])
