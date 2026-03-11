from sqlalchemy import Column, String, DateTime, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class SalesLedger(Base):
    __tablename__ = "sales_ledger"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    department = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional fields for audit analytics
    description = Column(String(500))
    currency = Column(String(10), default='USD')
    invoice_number = Column(String(100))
    payment_terms = Column(String(100))
    sales_person = Column(String(255))
    product_category = Column(String(100))
    quantity = Column(Numeric(10, 2))
    unit_price = Column(Numeric(15, 2))
    tax_amount = Column(Numeric(15, 2))
    total_amount = Column(Numeric(15, 2))