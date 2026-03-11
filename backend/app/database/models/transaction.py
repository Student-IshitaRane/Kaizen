from sqlalchemy import Column, String, DateTime, Numeric, Date, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database.session import Base

class TransactionType(str, enum.Enum):
    INVOICE = "invoice"
    PAYMENT = "payment"
    JOURNAL_ENTRY = "journal_entry"
    PURCHASE = "purchase"
    SALE = "sale"

class TransactionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTED = "posted"

class TransactionSource(str, enum.Enum):
    MANUAL = "manual"
    UPLOAD = "upload"
    IMPORT = "import"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    vendor_id = Column(String(100), ForeignKey('vendors.vendor_id', ondelete='SET NULL'), index=True)
    vendor_name = Column(String(255))
    amount = Column(Numeric(15, 2), nullable=False, index=True)
    currency = Column(String(10), default='USD')
    transaction_date = Column(Date, nullable=False, index=True)
    posting_date = Column(Date)
    description = Column(Text)
    department = Column(String(100))
    cost_center = Column(String(100))
    gl_account = Column(String(100))
    approver = Column(String(255))
    approval_date = Column(Date)
    reference_number = Column(String(100), index=True)
    invoice_number = Column(String(100))
    po_number = Column(String(100))
    payment_method = Column(String(50))
    bank_account = Column(String(100))
    status = Column(Enum(TransactionStatus), default=TransactionStatus.SUBMITTED, index=True)
    source = Column(Enum(TransactionSource), default=TransactionSource.MANUAL)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    transaction_metadata = Column(JSONB)
    
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    creator = relationship("User", foreign_keys=[created_by])
