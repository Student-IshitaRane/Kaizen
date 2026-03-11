from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

class PurchaseTransactionCreate(BaseModel):
    invoice_id: str
    vendor_id: str
    amount: Decimal
    invoice_date: date
    department: Optional[str] = None
    approver_id: Optional[str] = None
    description: Optional[str] = None
    currency: str = "USD"
    posting_date: Optional[date] = None
    cost_center: Optional[str] = None
    gl_account: Optional[str] = None
    approval_date: Optional[date] = None
    reference_number: Optional[str] = None
    po_number: Optional[str] = None
    payment_method: Optional[str] = None
    bank_account: Optional[str] = None

class PurchaseTransactionResponse(BaseModel):
    id: str
    invoice_id: str
    vendor_id: str
    amount: Decimal
    invoice_date: date
    department: Optional[str]
    approver_id: Optional[str]
    description: Optional[str]
    created_at: datetime
    analysis_summary: Optional[dict] = None
    
    class Config:
        orm_mode = True