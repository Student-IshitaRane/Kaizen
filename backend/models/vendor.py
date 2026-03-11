from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base
from core.constants import VendorStatus

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_code = Column(String(100), unique=True, nullable=False, index=True)
    vendor_name = Column(String(255), nullable=False, index=True)
    gst_number = Column(String(100))
    bank_account = Column(String(100))
    status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Additional fields for audit analytics
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(String(500))
    city = Column(String(100))
    country = Column(String(100))
    tax_id = Column(String(100))
    payment_terms = Column(String(100))