from sqlalchemy import Column, String, DateTime, Numeric, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.database.session import Base

class VendorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(String(100), unique=True, nullable=False, index=True)
    vendor_name = Column(String(255), nullable=False, index=True)
    vendor_type = Column(String(100))
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    tax_id = Column(String(100))
    payment_terms = Column(String(100))
    credit_limit = Column(Numeric(15, 2))
    status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_transaction_date = Column(DateTime(timezone=True))
    vendor_metadata = Column(JSONB)
