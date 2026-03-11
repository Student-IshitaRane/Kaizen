from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from core.constants import VendorStatus

class VendorCreate(BaseModel):
    vendor_code: str
    vendor_name: str
    gst_number: Optional[str] = None
    bank_account: Optional[str] = None
    status: VendorStatus = VendorStatus.ACTIVE
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None

class VendorResponse(BaseModel):
    id: str
    vendor_code: str
    vendor_name: str
    gst_number: Optional[str]
    bank_account: Optional[str]
    status: VendorStatus
    created_at: datetime
    
    class Config:
        orm_mode = True