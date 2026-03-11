from sqlalchemy import Column, String, DateTime, Numeric, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class GeneralLedger(Base):
    __tablename__ = "general_ledger"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id = Column(String(100), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False, index=True)
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    entry_date = Column(Date, nullable=False, index=True)
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional fields for audit analytics
    gl_account = Column(String(100), index=True)
    posting_date = Column(Date)
    fiscal_year = Column(Integer)
    fiscal_period = Column(Integer)
    document_number = Column(String(100))
    document_type = Column(String(50))
    cost_center = Column(String(100))
    profit_center = Column(String(100))
    currency = Column(String(10), default='USD')
    transaction_type = Column(String(50))