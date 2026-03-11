from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime
from database import get_db
from models.user import User
from schemas.dataset_upload import UploadResponse, UploadSummary
from auth.security import get_current_user, require_role
from core.constants import DatasetType, UserRole
from core.config import settings
from services.dataset_ingestion_service import DatasetIngestionService

router = APIRouter(prefix="/upload", tags=["Dataset Upload"])

@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload dataset file"""
    
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
    
    try:
        # Ingest dataset
        ingestion_service = DatasetIngestionService(db)
        inserted, failed, errors = ingestion_service.ingest_dataset(file_path, DatasetType.PURCHASE_LEDGER)
        
        status_msg = "completed"
        if failed > 0:
            status_msg = "partial"
        if inserted == 0:
            status_msg = "failed"
        
        return UploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            dataset_type=DatasetType.PURCHASE_LEDGER,
            rows_inserted=inserted,
            rows_failed=failed,
            status=status_msg,
            uploaded_at=datetime.utcnow()
        )
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process dataset: {str(e)}"
        )

@router.post("/dataset", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_type: DatasetType = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Upload historical dataset for analysis"""
    
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
    
    try:
        # Ingest dataset
        ingestion_service = DatasetIngestionService(db)
        inserted, failed, errors = ingestion_service.ingest_dataset(file_path, dataset_type)
        
        status_msg = "completed"
        if failed > 0:
            status_msg = "partial"
        if inserted == 0:
            status_msg = "failed"
        
        return UploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            dataset_type=dataset_type,
            rows_inserted=inserted,
            rows_failed=failed,
            status=status_msg,
            uploaded_at=datetime.utcnow()
        )
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process dataset: {str(e)}"
        )

@router.post("/test-ingestion", response_model=UploadSummary)
def test_dataset_ingestion(
    dataset_type: DatasetType,
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Test dataset ingestion with sample data"""
    
    try:
        # Create sample data based on dataset type
        import pandas as pd
        from io import StringIO
        
        if dataset_type == DatasetType.VENDOR_MASTER:
            sample_data = """vendor_code,vendor_name,gst_number,bank_account,contact_person,email,phone,address,city,country,tax_id,payment_terms
V001,ABC Corp,GST001,ACC001,John Doe,john@abc.com,1234567890,123 Main St,New York,USA,TAX001,Net 30
V002,XYZ Ltd,GST002,ACC002,Jane Smith,jane@xyz.com,0987654321,456 Oak Ave,Chicago,USA,TAX002,Net 45"""
        
        elif dataset_type == DatasetType.PURCHASE_LEDGER:
            sample_data = """invoice_id,vendor_id,amount,invoice_date,department,approver_id,description,currency,posting_date,cost_center,gl_account,approval_date,reference_number,po_number,payment_method,bank_account
INV-001,00000000-0000-0000-0000-000000000001,15000.00,2024-01-15,Operations,00000000-0000-0000-0000-000000000002,Office supplies,USD,2024-01-16,CC001,GL001,2024-01-14,REF001,PO001,bank transfer,ACC001
INV-002,00000000-0000-0000-0000-000000000002,25000.00,2024-01-20,IT,00000000-0000-0000-0000-000000000002,Software license,USD,2024-01-21,CC002,GL002,2024-01-19,REF002,PO002,credit card,ACC002"""
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sample data not available for dataset type: {dataset_type}"
            )
        
        # Create temporary file
        df = pd.read_csv(StringIO(sample_data))
        temp_file = f"/tmp/sample_{dataset_type}.csv"
        df.to_csv(temp_file, index=False)
        
        # Ingest sample data
        ingestion_service = DatasetIngestionService(db)
        inserted, failed, errors = ingestion_service.ingest_dataset(temp_file, dataset_type)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return UploadSummary(
            dataset_type=dataset_type,
            total_rows=inserted + failed,
            inserted_rows=inserted,
            failed_rows=failed,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test ingestion failed: {str(e)}"
        )