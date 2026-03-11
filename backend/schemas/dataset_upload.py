from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from core.constants import DatasetType

class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    dataset_type: DatasetType
    rows_inserted: int
    rows_failed: int
    status: str
    uploaded_at: datetime
    
    class Config:
        orm_mode = True

class UploadSummary(BaseModel):
    dataset_type: DatasetType
    total_rows: int
    inserted_rows: int
    failed_rows: int
    errors: list[str] = []