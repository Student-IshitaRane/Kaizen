from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from app.database.models import TransactionType, TransactionStatus

class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    amount: Decimal
    currency: str = "USD"
    transaction_date: date
    description: Optional[str] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    gl_account: Optional[str] = None
    approver: Optional[str] = None
    approval_date: Optional[date] = None
    reference_number: Optional[str] = None
    invoice_number: Optional[str] = None
    po_number: Optional[str] = None
    payment_method: Optional[str] = None
    bank_account: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TransactionResponse(BaseModel):
    id: str
    transaction_type: TransactionType
    vendor_id: Optional[str]
    vendor_name: Optional[str]
    amount: Decimal
    currency: str
    transaction_date: date
    description: Optional[str]
    department: Optional[str]
    reference_number: Optional[str]
    status: TransactionStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    page: int
    limit: int
