from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime
from app.database.session import get_db
from app.database.models import User, Upload, DatasetType, UploadStatus
from app.schemas.upload import UploadResponse, UploadStatusResponse, UploadHistoryResponse
from app.dependencies import get_current_user
from app.auth.permissions import is_auditor
from core.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/dataset", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_type: DatasetType = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_auditor(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only auditors can upload datasets"
        )
    
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    file_size = 0
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    upload_id = str(uuid.uuid4())
    filename = f"{upload_id}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    upload = Upload(
        id=upload_id,
        filename=file.filename,
        dataset_type=dataset_type,
        file_size=file_size,
        file_path=file_path,
        description=description,
        uploaded_by=current_user.id,
        uploaded_at=datetime.utcnow()
    )
    
    db.add(upload)
    db.commit()
    db.refresh(upload)
    
    return UploadResponse(
        upload_id=upload.id,
        filename=upload.filename,
        dataset_type=upload.dataset_type,
        status=upload.status,
        rows_count=None,
        uploaded_at=upload.uploaded_at
    )

@router.get("/{upload_id}/status", response_model=UploadStatusResponse)
def get_upload_status(
    upload_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    if upload.uploaded_by != current_user.id and not is_auditor(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    progress = 0
    if upload.rows_total and upload.rows_processed:
        progress = int((upload.rows_processed / upload.rows_total) * 100)
    
    return UploadStatusResponse(
        upload_id=upload.id,
        status=upload.status,
        progress=progress,
        rows_processed=upload.rows_processed,
        errors=upload.error_log or []
    )

@router.get("/history", response_model=UploadHistoryResponse)
def get_upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if is_auditor(current_user.role):
        uploads = db.query(Upload).filter(Upload.uploaded_by == current_user.id).order_by(Upload.uploaded_at.desc()).all()
    else:
        uploads = []
    
    return UploadHistoryResponse(
        uploads=[
            UploadResponse(
                upload_id=upload.id,
                filename=upload.filename,
                dataset_type=upload.dataset_type,
                status=upload.status,
                rows_count=upload.rows_total,
                uploaded_at=upload.uploaded_at
            )
            for upload in uploads
        ]
    )