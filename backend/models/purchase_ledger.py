from sqlalchemy import Column, String, DateTime, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base

class PurchaseLedger(Base):
    __tablename__ = "purchase_ledger"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(String(100), unique=True, nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.id'), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    department = Column(String(100))
    approver_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional fields for audit analytics
    currency = Column(String(10), default='USD')
    posting_date = Column(Date)
    cost_center = Column(String(100))
    gl_account = Column(String(100))
    approval_date = Column(Date)
    reference_number = Column(String(100))
    po_number = Column(String(100))
    payment_method = Column(String(50))
    bank_account = Column(String(100))
    status = Column(String(50), default='submitted')
    
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    approver = relationship("User", foreign_keys=[approver_id])