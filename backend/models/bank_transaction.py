from sqlalchemy import Column, String, DateTime, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base

class BankTransaction(Base):
    __tablename__ = "bank_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    account_number = Column(String(100), nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.id'), nullable=True, index=True)
    amount = Column(Numeric(15, 2), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)
    reference = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional fields for audit analytics
    value_date = Column(Date)
    currency = Column(String(10), default='USD')
    description = Column(String(500))
    counterparty_name = Column(String(255))
    counterparty_account = Column(String(100))
    balance_after = Column(Numeric(15, 2))
    bank_name = Column(String(100))
    branch_code = Column(String(50))
    payment_method = Column(String(50))
    
    vendor = relationship("Vendor", foreign_keys=[vendor_id])