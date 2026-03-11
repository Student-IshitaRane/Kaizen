from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.database.models import DatasetType, UploadStatus

class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    dataset_type: DatasetType
    status: UploadStatus
    rows_count: Optional[int] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class UploadStatusResponse(BaseModel):
    upload_id: str
    status: UploadStatus
    progress: int
    rows_processed: Optional[int] = None
    errors: list = []
    
    class Config:
        from_attributes = True

class UploadHistoryResponse(BaseModel):
    uploads: list[UploadResponse]
