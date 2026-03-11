from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.user import User
from schemas.flagged_case import FlaggedCaseListResponse, FlaggedCaseDetailResponse
from auth.security import get_current_user, require_role
from core.constants import UserRole, CaseStatus, RiskLevel, FlagType
from services.flagged_case_service import FlaggedCaseService

router = APIRouter(prefix="/cases", tags=["Flagged Cases"])

@router.get("", response_model=FlaggedCaseListResponse)
def list_cases(
    status: Optional[CaseStatus] = None,
    risk_level: Optional[RiskLevel] = None,
    flag_type: Optional[FlagType] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """List flagged cases with filtering (Auditors only)"""
    
    try:
        case_service = FlaggedCaseService(db)
        
        result = case_service.get_cases(
            status=status,
            risk_level=risk_level,
            flag_type=flag_type,
            page=page,
            limit=limit
        )
        
        return FlaggedCaseListResponse(
            cases=result["cases"],
            total=result["total"],
            page=result["page"],
            limit=result["limit"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch cases: {str(e)}"
        )

@router.get("/{case_id}", response_model=FlaggedCaseDetailResponse)
def get_case_details(
    case_id: str,
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Get flagged case details by ID (Auditors only)"""
    
    try:
        case_service = FlaggedCaseService(db)
        case = case_service.get_case_by_id(case_id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        return FlaggedCaseDetailResponse.from_orm(case)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch case details: {str(e)}"
        )

@router.post("/{case_id}/assign")
def assign_case(
    case_id: str,
    auditor_id: str,
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Assign case to auditor (Auditors only)"""
    
    try:
        case_service = FlaggedCaseService(db)
        case = case_service.assign_case(case_id, auditor_id)
        
        return {
            "case_id": str(case.id),
            "assigned_to": auditor_id,
            "assigned_at": case.assigned_at.isoformat() if case.assigned_at else None,
            "message": "Case assigned successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign case: {str(e)}"
        )

@router.get("/statistics/summary")
def get_case_statistics(
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Get case statistics for dashboard (Auditors only)"""
    
    try:
        case_service = FlaggedCaseService(db)
        statistics = case_service.get_case_statistics()
        
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )

@router.post("/test-flag")
def test_flag_case(
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Create a test flagged case for demonstration"""
    
    try:
        case_service = FlaggedCaseService(db)
        
        # Create a test case
        case = case_service.create_case(
            transaction_type="purchase",
            transaction_ref_id="INV-TEST-001",
            flag_type=FlagType.DUPLICATE_INVOICE,
            risk_score=85,
            risk_level=RiskLevel.HIGH,
            reason_summary="Duplicate invoice detected with same amount and vendor",
            vendor_id=None,  # Would be actual vendor ID in production
            transaction_amount=15000.00,
            transaction_date="2024-01-15",
            department="Operations",
            approver="John Smith",
            explanation="This invoice appears to be a duplicate of INV-001 submitted on 2024-01-10",
            recommendation="Verify with vendor and check payment records"
        )
        
        return {
            "case_id": str(case.id),
            "message": "Test case created successfully",
            "case": FlaggedCaseDetailResponse.from_orm(case)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test case: {str(e)}"
        )