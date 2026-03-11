from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.review_action import ReviewActionRequest, ReviewActionResponse
from auth.security import get_current_user, require_role
from core.constants import UserRole
from services.flagged_case_service import FlaggedCaseService

router = APIRouter(prefix="/reviews", tags=["Review Actions"])

@router.post("/{case_id}", response_model=ReviewActionResponse)
def review_case(
    case_id: str,
    review_data: ReviewActionRequest,
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Review a flagged case and update its status (Auditors only)"""
    
    try:
        case_service = FlaggedCaseService(db)
        
        case = case_service.update_case_status(
            case_id=case_id,
            status=review_data.decision,
            auditor_id=str(current_user.id),
            comments=review_data.comments,
            action_taken=review_data.action_taken,
            evidence_reviewed=review_data.evidence_reviewed,
            follow_up_required=review_data.follow_up_required,
            follow_up_date=review_data.follow_up_date
        )
        
        # Get the latest review action
        from models.review_action import ReviewAction
        review_action = db.query(ReviewAction).filter(
            ReviewAction.case_id == case_id,
            ReviewAction.auditor_id == current_user.id
        ).order_by(ReviewAction.reviewed_at.desc()).first()
        
        if not review_action:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Review action not found after creation"
            )
        
        return ReviewActionResponse.from_orm(review_action)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to review case: {str(e)}"
        )

@router.get("/{case_id}/history")
def get_review_history(
    case_id: str,
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Get review history for a case (Auditors only)"""
    
    try:
        from models.review_action import ReviewAction
        
        # Verify case exists
        case_service = FlaggedCaseService(db)
        case = case_service.get_case_by_id(case_id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        # Get review history
        reviews = db.query(ReviewAction).filter(
            ReviewAction.case_id == case_id
        ).order_by(ReviewAction.reviewed_at.desc()).all()
        
        return {
            "case_id": case_id,
            "case_status": case.status.value,
            "review_history": [
                {
                    "id": str(review.id),
                    "auditor_id": str(review.auditor_id),
                    "auditor_name": review.auditor.name if review.auditor else None,
                    "decision": review.decision.value,
                    "comments": review.comments,
                    "action_taken": review.action_taken,
                    "evidence_reviewed": review.evidence_reviewed,
                    "follow_up_required": review.follow_up_required,
                    "follow_up_date": review.follow_up_date.isoformat() if review.follow_up_date else None,
                    "reviewed_at": review.reviewed_at.isoformat()
                }
                for review in reviews
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch review history: {str(e)}"
        )

@router.get("/auditor/{auditor_id}/summary")
def get_auditor_review_summary(
    auditor_id: str,
    current_user: User = Depends(require_role(UserRole.AUDITOR)),
    db: Session = Depends(get_db)
):
    """Get review summary for an auditor (Auditors only)"""
    
    try:
        from models.review_action import ReviewAction
        from sqlalchemy import func
        
        # Verify auditor exists and is an auditor
        auditor = db.query(User).filter(
            User.id == auditor_id,
            User.role.in_(["auditor", "admin"])
        ).first()
        
        if not auditor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auditor not found"
            )
        
        # Get review statistics
        total_reviews = db.query(ReviewAction).filter(
            ReviewAction.auditor_id == auditor_id
        ).count()
        
        # Get decision distribution
        from core.constants import CaseStatus
        decision_counts = {}
        for status in CaseStatus:
            count = db.query(ReviewAction).filter(
                ReviewAction.auditor_id == auditor_id,
                ReviewAction.decision == status
            ).count()
            decision_counts[status.value] = count
        
        # Get recent reviews
        recent_reviews = db.query(ReviewAction).filter(
            ReviewAction.auditor_id == auditor_id
        ).order_by(ReviewAction.reviewed_at.desc()).limit(10).all()
        
        return {
            "auditor": {
                "id": str(auditor.id),
                "name": auditor.name,
                "email": auditor.email,
                "role": auditor.role.value
            },
            "statistics": {
                "total_reviews": total_reviews,
                "decision_distribution": decision_counts
            },
            "recent_reviews": [
                {
                    "case_id": str(review.case_id),
                    "decision": review.decision.value,
                    "reviewed_at": review.reviewed_at.isoformat()
                }
                for review in recent_reviews
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch auditor summary: {str(e)}"
        )