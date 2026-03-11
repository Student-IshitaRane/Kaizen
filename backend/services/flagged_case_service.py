from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime
import uuid
from core.constants import CaseStatus, RiskLevel, FlagType
from models.flagged_case import FlaggedCase
from models.review_action import ReviewAction
from models.user import User

class FlaggedCaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_cases(
        self,
        status: Optional[CaseStatus] = None,
        risk_level: Optional[RiskLevel] = None,
        flag_type: Optional[FlagType] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get flagged cases with filtering and pagination"""
        
        query = self.db.query(FlaggedCase)
        
        if status:
            query = query.filter(FlaggedCase.status == status)
        if risk_level:
            query = query.filter(FlaggedCase.risk_level == risk_level)
        if flag_type:
            query = query.filter(FlaggedCase.flag_type == flag_type)
        
        total = query.count()
        
        cases = query.order_by(desc(FlaggedCase.created_at)) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()
        
        return {
            "cases": cases,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    def get_case_by_id(self, case_id: str) -> Optional[FlaggedCase]:
        """Get flagged case by ID"""
        return self.db.query(FlaggedCase).filter(FlaggedCase.id == case_id).first()
    
    def create_case(
        self,
        transaction_type: str,
        transaction_ref_id: str,
        flag_type: FlagType,
        risk_score: int,
        risk_level: RiskLevel,
        reason_summary: str,
        vendor_id: Optional[str] = None,
        transaction_amount: Optional[float] = None,
        transaction_date: Optional[datetime] = None,
        department: Optional[str] = None,
        approver: Optional[str] = None,
        explanation: Optional[str] = None,
        recommendation: Optional[str] = None
    ) -> FlaggedCase:
        """Create a new flagged case"""
        
        case = FlaggedCase(
            id=uuid.uuid4(),
            transaction_type=transaction_type,
            transaction_ref_id=transaction_ref_id,
            vendor_id=uuid.UUID(vendor_id) if vendor_id else None,
            flag_type=flag_type,
            risk_score=risk_score,
            risk_level=risk_level,
            reason_summary=reason_summary,
            transaction_amount=transaction_amount,
            transaction_date=transaction_date,
            department=department,
            approver=approver,
            explanation=explanation,
            recommendation=recommendation,
            status=CaseStatus.PENDING
        )
        
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        
        return case
    
    def update_case_status(
        self,
        case_id: str,
        status: CaseStatus,
        auditor_id: str,
        comments: Optional[str] = None,
        action_taken: Optional[str] = None,
        evidence_reviewed: Optional[str] = None,
        follow_up_required: bool = False,
        follow_up_date: Optional[datetime] = None
    ) -> FlaggedCase:
        """Update case status and create review action"""
        
        case = self.get_case_by_id(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")
        
        # Update case
        case.status = status
        case.reviewed_by = uuid.UUID(auditor_id)
        case.reviewed_at = datetime.utcnow()
        case.review_notes = comments
        case.action_taken = action_taken
        
        if status == CaseStatus.RESOLVED:
            case.resolved_at = datetime.utcnow()
        
        # Create review action
        review_action = ReviewAction(
            id=uuid.uuid4(),
            case_id=uuid.UUID(case_id),
            auditor_id=uuid.UUID(auditor_id),
            decision=status,
            comments=comments,
            action_taken=action_taken,
            evidence_reviewed=evidence_reviewed,
            follow_up_required=follow_up_required,
            follow_up_date=follow_up_date
        )
        
        self.db.add(review_action)
        self.db.commit()
        self.db.refresh(case)
        
        return case
    
    def assign_case(self, case_id: str, auditor_id: str) -> FlaggedCase:
        """Assign case to auditor"""
        
        case = self.get_case_by_id(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")
        
        # Verify auditor exists and is an auditor
        auditor = self.db.query(User).filter(
            User.id == auditor_id,
            User.role.in_(["auditor", "admin"])
        ).first()
        
        if not auditor:
            raise ValueError(f"Invalid auditor ID: {auditor_id}")
        
        case.assigned_to = uuid.UUID(auditor_id)
        case.assigned_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(case)
        
        return case
    
    def get_case_statistics(self) -> Dict[str, Any]:
        """Get case statistics for dashboard"""
        
        total_cases = self.db.query(FlaggedCase).count()
        
        status_counts = {}
        for status in CaseStatus:
            count = self.db.query(FlaggedCase).filter(FlaggedCase.status == status).count()
            status_counts[status.value] = count
        
        risk_counts = {}
        for risk in RiskLevel:
            count = self.db.query(FlaggedCase).filter(FlaggedCase.risk_level == risk).count()
            risk_counts[risk.value] = count
        
        flag_type_counts = {}
        for flag_type in FlagType:
            count = self.db.query(FlaggedCase).filter(FlaggedCase.flag_type == flag_type).count()
            flag_type_counts[flag_type.value] = count
        
        return {
            "total_cases": total_cases,
            "status_distribution": status_counts,
            "risk_distribution": risk_counts,
            "flag_type_distribution": flag_type_counts
        }