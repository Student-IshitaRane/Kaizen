from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.database.session import get_db
from app.database.models import User, FlaggedTransaction, CaseStatus, RiskLevel, Transaction
from app.schemas.case import (
    CaseListResponse, CaseDetailResponse, CaseReviewRequest, 
    CaseReviewResponse, CaseAssignRequest, CaseAssignResponse,
    CaseAnalysisDetailResponse
)
from app.dependencies import get_current_user
from app.auth.permissions import is_auditor
from services.analysis_result_service import AnalysisResultService

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.get("", response_model=CaseListResponse)
def list_cases(
    status: Optional[CaseStatus] = None,
    risk_level: Optional[RiskLevel] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_auditor(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only auditors can view cases"
        )
    
    query = db.query(FlaggedTransaction)
    
    if status:
        query = query.filter(FlaggedTransaction.status == status)
    if risk_level:
        query = query.filter(FlaggedTransaction.risk_level == risk_level)
    
    total = query.count()
    
    cases = query.order_by(desc(FlaggedTransaction.flagged_at)) \
        .offset((page - 1) * limit) \
        .limit(limit) \
        .all()
    
    return CaseListResponse(
        cases=[
            {
                "case_id": str(case.id),
                "case_number": case.case_number,
                "transaction_id": str(case.transaction_id),
                "vendor_name": case.transaction.vendor_name if case.transaction else None,
                "amount": case.transaction.amount if case.transaction else 0,
                "risk_score": case.risk_score,
                "risk_level": case.risk_level,
                "flags": [flag.get("type", "") for flag in case.flags] if case.flags else [],
                "status": case.status,
                "flagged_at": case.flagged_at
            }
            for case in cases
        ],
        total=total,
        page=page,
        limit=limit
    )

@router.get("/{case_id}", response_model=CaseDetailResponse)
def get_case_details(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_auditor(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only auditors can view case details"
        )
    
    case = db.query(FlaggedTransaction).filter(FlaggedTransaction.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    transaction = case.transaction
    
    return CaseDetailResponse(
        case_id=str(case.id),
        case_number=case.case_number,
        transaction={
            "transaction_id": str(transaction.id),
            "vendor_id": transaction.vendor_id,
            "vendor_name": transaction.vendor_name,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "transaction_date": transaction.transaction_date,
            "description": transaction.description,
            "department": transaction.department,
            "reference_number": transaction.reference_number
        },
        risk_score=case.risk_score,
        risk_level=case.risk_level,
        flags=[
            {
                "type": flag.get("type", ""),
                "severity": flag.get("severity", "medium"),
                "description": flag.get("description", ""),
                "evidence": flag.get("evidence")
            }
            for flag in case.flags
        ] if case.flags else [],
        explanation=case.explanation,
        recommendation=case.recommendation,
        status=case.status,
        assigned_to=case.assignee.email if case.assignee else None,
        flagged_at=case.flagged_at,
        reviewed_at=case.reviewed_at,
        review_notes=case.review_notes
    )

@router.put("/{case_id}/review", response_model=CaseReviewResponse)
def review_case(
    case_id: str,
    review_data: CaseReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_auditor(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only auditors can review cases"
        )
    
    case = db.query(FlaggedTransaction).filter(FlaggedTransaction.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    case.status = review_data.status
    case.reviewed_by = current_user.id
    case.reviewed_at = datetime.utcnow()
    case.review_notes = review_data.notes
    case.action_taken = review_data.action_taken
    
    if review_data.status == CaseStatus.RESOLVED:
        case.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(case)
    
    return CaseReviewResponse(
        case_id=str(case.id),
        status=case.status,
        reviewed_by=current_user.email,
        reviewed_at=case.reviewed_at
    )

@router.post("/{case_id}/assign", response_model=CaseAssignResponse)
def assign_case(
    case_id: str,
    assign_data: CaseAssignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_auditor(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only auditors can assign cases"
        )
    
    case = db.query(FlaggedTransaction).filter(FlaggedTransaction.id == case_id).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    assignee = db.query(User).filter(User.id == assign_data.auditor_id).first()
    
    if not assignee or not is_auditor(assignee.role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid auditor ID"
        )
    
    case.assigned_to = assignee.id
    case.assigned_at = datetime.utcnow()
    
    db.commit()
    db.refresh(case)
    
    return CaseAssignResponse(
        case_id=str(case.id),
        assigned_to=assignee.email,
        assigned_at=case.assigned_at
    )

@router.get("/{case_id}/analysis", response_model=CaseAnalysisDetailResponse)
def get_case_analysis_details(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analysis information for a flagged case"""
    if not is_auditor(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only auditors can view case analysis details"
        )
    
    # Use AnalysisResultService to get detailed analysis
    analysis_service = AnalysisResultService(db)
    analysis_details = analysis_service.get_case_analysis_details(case_id)
    
    if not analysis_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case analysis details not found"
        )
    
    # Convert to response model
    case_data = analysis_details["case"]
    transaction_data = analysis_details["transaction"]
    vendor_data = analysis_details["vendor"]
    analysis_metadata = analysis_details["analysis_metadata"]
    
    # Extract scoring breakdown from metadata
    scoring_breakdown = analysis_metadata.get("scoring_breakdown", {})
    
    # Extract suggested actions
    suggested_actions = []
    if case_data.get("suggested_actions"):
        for action in case_data["suggested_actions"]:
            if isinstance(action, dict):
                suggested_actions.append({
                    "action": action.get("action", ""),
                    "rationale": action.get("rationale", ""),
                    "priority": action.get("priority", "medium"),
                    "expected_outcome": action.get("expected_outcome", "")
                })
            elif isinstance(action, str):
                suggested_actions.append({
                    "action": action,
                    "rationale": "Generated by analysis system",
                    "priority": "medium",
                    "expected_outcome": "Complete review and documentation"
                })
    
    # Prepare scoring breakdown
    analysis_scoring_breakdown = AnalysisScoringBreakdown(
        anomaly_scores=scoring_breakdown.get("anomaly_scores", []),
        pattern_scores=scoring_breakdown.get("pattern_scores", []),
        validation_scores=scoring_breakdown.get("validation_scores", []),
        category_totals=scoring_breakdown.get("category_totals", {}),
        detailed_scores=scoring_breakdown.get("detailed_scores", {})
    )
    
    # Prepare transaction detail
    transaction_detail = TransactionDetail(
        transaction_id=transaction_data.get("invoice_id", ""),
        vendor_id=vendor_data.get("id") if vendor_data else None,
        vendor_name=vendor_data.get("vendor_name") if vendor_data else None,
        amount=transaction_data.get("amount", 0),
        currency=transaction_data.get("currency", "USD"),
        transaction_date=datetime.fromisoformat(transaction_data["invoice_date"]).date() if transaction_data.get("invoice_date") else datetime.utcnow().date(),
        description=transaction_data.get("description"),
        department=transaction_data.get("department"),
        reference_number=transaction_data.get("reference_number")
    )
    
    return CaseAnalysisDetailResponse(
        case_id=case_data["id"],
        case_number=case_data["case_id"],
        transaction=transaction_detail,
        risk_score=case_data["risk_score"],
        risk_level=case_data["risk_level"],
        flag_type=case_data["flag_type"],
        reason_summary=case_data["reason_summary"],
        detailed_explanation=case_data["detailed_explanation"],
        suggested_actions=suggested_actions,
        scoring_breakdown=analysis_scoring_breakdown,
        analysis_metadata=analysis_metadata,
        status=case_data["status"],
        priority=case_data["priority"],
        assigned_to=analysis_details["assigned_to"]["name"] if analysis_details.get("assigned_to") else None,
        created_at=datetime.fromisoformat(case_data["created_at"]) if case_data.get("created_at") else datetime.utcnow(),
        updated_at=datetime.fromisoformat(case_data["updated_at"]) if case_data.get("updated_at") else datetime.utcnow(),
        review_notes=case_data["review_notes"],
        resolution=case_data["resolution"],
        resolved_at=datetime.fromisoformat(case_data["resolved_at"]) if case_data.get("resolved_at") else None
    )