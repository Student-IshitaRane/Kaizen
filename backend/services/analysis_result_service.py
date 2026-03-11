import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid

from app.database.session import get_db
from app.database.models.flagged_transaction import FlaggedTransaction
from app.database.models.transaction import Transaction
from app.database.models.vendor import Vendor
from app.database.models.user import User
from core.config import settings

logger = logging.getLogger(__name__)


class AnalysisResultService:
    """Service for mapping analysis results to FlaggedCase creation and management"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
    
    def create_flagged_case_from_analysis(self, 
                                         transaction_data: Dict[str, Any],
                                         analysis_results: Dict[str, Any],
                                         pipeline_results: Dict[str, Any]) -> Optional[FlaggedTransaction]:
        """
        Create a flagged case from analysis results
        
        Args:
            transaction_data: Original transaction data
            analysis_results: Results from agent analysis
            pipeline_results: Complete pipeline execution results
            
        Returns:
            FlaggedTransaction object if created, None otherwise
        """
        try:
            if not self.db:
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            # Check if we should create a flagged case
            should_flag = self._should_create_flagged_case(analysis_results, pipeline_results)
            if not should_flag:
                logger.info(f"No flagged case needed for transaction {transaction_data.get('invoice_id')}")
                return None
            
            # Get or create transaction record
            transaction = self._get_or_create_transaction(transaction_data)
            if not transaction:
                logger.error(f"Failed to get/create transaction for {transaction_data.get('invoice_id')}")
                return None
            
            # Check if flagged case already exists
            existing_case = self.db.query(FlaggedTransaction).filter(
                FlaggedTransaction.transaction_id == transaction.id
            ).first()
            
            if existing_case:
                logger.info(f"Flagged case already exists for transaction {transaction.id}")
                return self._update_existing_case(existing_case, analysis_results, pipeline_results)
            
            # Create new flagged case
            flagged_case = self._create_new_flagged_case(
                transaction, transaction_data, analysis_results, pipeline_results
            )
            
            self.db.add(flagged_case)
            self.db.commit()
            self.db.refresh(flagged_case)
            
            logger.info(f"Created flagged case {flagged_case.id} for transaction {transaction.id}")
            
            return flagged_case
            
        except Exception as e:
            logger.error(f"Failed to create flagged case: {str(e)}")
            if self.db:
                self.db.rollback()
            return None
    
    def _should_create_flagged_case(self, 
                                   analysis_results: Dict[str, Any],
                                   pipeline_results: Dict[str, Any]) -> bool:
        """Determine if a flagged case should be created"""
        # Check pipeline flag recommendation
        if pipeline_results.get("flag_recommendation", False):
            return True
        
        # Check risk scoring recommendation
        risk_scoring = analysis_results.get("risk_scoring", {})
        if risk_scoring.get("flag_recommendation", False):
            return True
        
        # Check for high risk level
        if risk_scoring.get("risk_level") == "high":
            return True
        
        # Check for critical findings
        anomaly_results = analysis_results.get("anomaly_detection", {})
        validation_results = analysis_results.get("rule_validation", {})
        
        if anomaly_results.get("summary", {}).get("high_severity_count", 0) > 0:
            return True
        
        if validation_results.get("control_summary", {}).get("high_severity_failures", 0) > 0:
            return True
        
        # Check for exact duplicate
        anomalies = anomaly_results.get("anomalies", [])
        for anomaly in anomalies:
            if anomaly.get("type") == "exact_duplicate_invoice":
                return True
        
        return False
    
    def _get_or_create_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Transaction]:
        """Get existing transaction or create new one"""
        try:
            invoice_id = transaction_data.get("invoice_id")
            vendor_id = transaction_data.get("vendor_id")
            
            if not invoice_id or not vendor_id:
                logger.warning("Missing invoice_id or vendor_id for transaction creation")
                return None
            
            # Try to find existing transaction
            transaction = self.db.query(Transaction).filter(
                Transaction.invoice_id == invoice_id,
                Transaction.vendor_id == vendor_id
            ).first()
            
            if transaction:
                return transaction
            
            # Create new transaction
            transaction = Transaction(
                invoice_id=invoice_id,
                vendor_id=vendor_id,
                amount=transaction_data.get("amount"),
                currency=transaction_data.get("currency", "USD"),
                invoice_date=self._parse_date(transaction_data.get("invoice_date")),
                posting_date=self._parse_date(transaction_data.get("posting_date")),
                department=transaction_data.get("department"),
                description=transaction_data.get("description", ""),
                status="pending_review",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to get/create transaction: {str(e)}")
            return None
    
    def _create_new_flagged_case(self, 
                                transaction: Transaction,
                                transaction_data: Dict[str, Any],
                                analysis_results: Dict[str, Any],
                                pipeline_results: Dict[str, Any]) -> FlaggedTransaction:
        """Create a new flagged case"""
        
        # Extract key analysis data
        risk_scoring = analysis_results.get("risk_scoring", {})
        explanation = analysis_results.get("explanation_generation", {})
        anomaly_results = analysis_results.get("anomaly_detection", {})
        pattern_results = analysis_results.get("pattern_analysis", {})
        validation_results = analysis_results.get("rule_validation", {})
        
        # Determine flag type
        flag_type = self._determine_flag_type(
            risk_scoring, anomaly_results, validation_results
        )
        
        # Get explanation data
        explanation_data = explanation.get("explanation", {}) if explanation else {}
        
        # Create flagged case
        flagged_case = FlaggedTransaction(
            case_id=f"FLG-{uuid.uuid4().hex[:8].upper()}",
            transaction_id=transaction.id,
            transaction_type="purchase",
            transaction_ref_id=transaction_data.get("invoice_id"),
            vendor_id=transaction_data.get("vendor_id"),
            flag_type=flag_type,
            risk_score=risk_scoring.get("overall_risk_score", 0),
            risk_level=risk_scoring.get("risk_level", "unknown"),
            reason_summary=explanation_data.get("reason_summary", ""),
            detailed_explanation=explanation_data.get("detailed_explanation", ""),
            suggested_actions=explanation_data.get("suggested_actions", []),
            status="new",
            priority=self._determine_priority(risk_scoring.get("risk_level", "unknown")),
            assigned_to=None,
            review_notes="",
            resolution="",
            resolved_by=None,
            resolved_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            
            # Store analysis metadata
            analysis_metadata={
                "pipeline_id": pipeline_results.get("pipeline_id"),
                "pipeline_name": pipeline_results.get("pipeline_name"),
                "processing_time_ms": pipeline_results.get("processing_time_ms", 0),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "scoring_breakdown": risk_scoring.get("scoring_breakdown", {}),
                "anomaly_summary": anomaly_results.get("summary", {}),
                "pattern_summary": pattern_results.get("summary", {}),
                "validation_summary": validation_results.get("control_summary", {})
            }
        )
        
        return flagged_case
    
    def _update_existing_case(self, 
                             flagged_case: FlaggedTransaction,
                             analysis_results: Dict[str, Any],
                             pipeline_results: Dict[str, Any]) -> FlaggedTransaction:
        """Update existing flagged case with new analysis results"""
        
        risk_scoring = analysis_results.get("risk_scoring", {})
        explanation = analysis_results.get("explanation_generation", {})
        
        # Update risk score and level if higher
        new_score = risk_scoring.get("overall_risk_score", 0)
        new_level = risk_scoring.get("risk_level", "unknown")
        
        if new_score > flagged_case.risk_score:
            flagged_case.risk_score = new_score
            flagged_case.risk_level = new_level
        
        # Update explanation if available
        if explanation and explanation.get("explanation"):
            explanation_data = explanation["explanation"]
            flagged_case.reason_summary = explanation_data.get("reason_summary", flagged_case.reason_summary)
            flagged_case.detailed_explanation = explanation_data.get("detailed_explanation", flagged_case.detailed_explanation)
            flagged_case.suggested_actions = explanation_data.get("suggested_actions", flagged_case.suggested_actions)
        
        # Update analysis metadata
        if not flagged_case.analysis_metadata:
            flagged_case.analysis_metadata = {}
        
        flagged_case.analysis_metadata.update({
            "updated_analysis_timestamp": datetime.utcnow().isoformat(),
            "latest_pipeline_id": pipeline_results.get("pipeline_id"),
            "latest_risk_score": new_score,
            "latest_risk_level": new_level
        })
        
        flagged_case.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(flagged_case)
        
        logger.info(f"Updated flagged case {flagged_case.id} with new analysis")
        
        return flagged_case
    
    def _determine_flag_type(self, 
                            risk_scoring: Dict[str, Any],
                            anomaly_results: Dict[str, Any],
                            validation_results: Dict[str, Any]) -> str:
        """Determine the type of flag based on findings"""
        
        # Check for exact duplicate
        anomalies = anomaly_results.get("anomalies", [])
        for anomaly in anomalies:
            if anomaly.get("type") == "exact_duplicate_invoice":
                return "duplicate_payment"
        
        # Check for high severity validation failures
        validation_summary = validation_results.get("control_summary", {})
        if validation_summary.get("high_severity_failures", 0) > 0:
            return "compliance_violation"
        
        # Check for threshold avoidance
        for anomaly in anomalies:
            if anomaly.get("type") == "threshold_avoidance":
                return "threshold_avoidance"
        
        # Check risk level
        risk_level = risk_scoring.get("risk_level", "unknown")
        if risk_level == "high":
            return "high_risk_transaction"
        elif risk_level == "medium":
            return "medium_risk_transaction"
        else:
            return "routine_review"
    
    def _determine_priority(self, risk_level: str) -> str:
        """Determine priority based on risk level"""
        priority_map = {
            "high": "high",
            "medium": "medium", 
            "low": "low"
        }
        return priority_map.get(risk_level, "low")
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date from various formats"""
        if isinstance(date_value, datetime):
            return date_value
        elif isinstance(date_value, str):
            try:
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError:
                formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"]
                for fmt in formats:
                    try:
                        return datetime.strptime(date_value, fmt)
                    except ValueError:
                        continue
        return None
    
    def get_flagged_cases(self, 
                         filters: Dict[str, Any] = None,
                         limit: int = 100,
                         offset: int = 0) -> List[FlaggedTransaction]:
        """Get flagged cases with optional filters"""
        try:
            if not self.db:
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            query = self.db.query(FlaggedTransaction)
            
            # Apply filters
            if filters:
                if filters.get("status"):
                    query = query.filter(FlaggedTransaction.status == filters["status"])
                
                if filters.get("risk_level"):
                    query = query.filter(FlaggedTransaction.risk_level == filters["risk_level"])
                
                if filters.get("priority"):
                    query = query.filter(FlaggedTransaction.priority == filters["priority"])
                
                if filters.get("flag_type"):
                    query = query.filter(FlaggedTransaction.flag_type == filters["flag_type"])
                
                if filters.get("vendor_id"):
                    query = query.filter(FlaggedTransaction.vendor_id == filters["vendor_id"])
                
                if filters.get("assigned_to"):
                    query = query.filter(FlaggedTransaction.assigned_to == filters["assigned_to"])
                
                if filters.get("date_from"):
                    query = query.filter(FlaggedTransaction.created_at >= filters["date_from"])
                
                if filters.get("date_to"):
                    query = query.filter(FlaggedTransaction.created_at <= filters["date_to"])
            
            # Apply ordering and pagination
            query = query.order_by(
                FlaggedTransaction.priority.desc(),
                FlaggedTransaction.risk_score.desc(),
                FlaggedTransaction.created_at.desc()
            )
            
            return query.offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Failed to get flagged cases: {str(e)}")
            return []
    
    def update_case_status(self, 
                          case_id: int,
                          status: str,
                          review_notes: str = "",
                          resolution: str = "",
                          resolved_by: int = None) -> Optional[FlaggedTransaction]:
        """Update flagged case status"""
        try:
            if not self.db:
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            case = self.db.query(FlaggedTransaction).filter(FlaggedTransaction.id == case_id).first()
            if not case:
                logger.error(f"Flagged case {case_id} not found")
                return None
            
            case.status = status
            case.review_notes = review_notes
            case.updated_at = datetime.utcnow()
            
            if status in ["resolved", "closed", "dismissed"]:
                case.resolution = resolution
                case.resolved_by = resolved_by
                case.resolved_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(case)
            
            logger.info(f"Updated case {case_id} status to {status}")
            
            return case
            
        except Exception as e:
            logger.error(f"Failed to update case status: {str(e)}")
            if self.db:
                self.db.rollback()
            return None
    
    def assign_case(self, case_id: int, user_id: int) -> Optional[FlaggedTransaction]:
        """Assign flagged case to a user"""
        try:
            if not self.db:
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            case = self.db.query(FlaggedTransaction).filter(FlaggedTransaction.id == case_id).first()
            if not case:
                logger.error(f"Flagged case {case_id} not found")
                return None
            
            # Verify user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            case.assigned_to = user_id
            case.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(case)
            
            logger.info(f"Assigned case {case_id} to user {user_id}")
            
            return case
            
        except Exception as e:
            logger.error(f"Failed to assign case: {str(e)}")
            if self.db:
                self.db.rollback()
            return None
    
    def get_case_analysis_details(self, case_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed analysis information for a flagged case"""
        try:
            if not self.db:
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            case = self.db.query(FlaggedTransaction).filter(FlaggedTransaction.id == case_id).first()
            if not case:
                logger.error(f"Flagged case {case_id} not found")
                return None
            
            # Get transaction details
            transaction = self.db.query(Transaction).filter(Transaction.id == case.transaction_id).first()
            
            # Get vendor details
            vendor = None
            if case.vendor_id:
                vendor = self.db.query(Vendor).filter(Vendor.id == case.vendor_id).first()
            
            # Get assigned user details
            assigned_user = None
            if case.assigned_to:
                assigned_user = self.db.query(User).filter(User.id == case.assigned_to).first()
            
            # Get resolved user details
            resolved_user = None
            if case.resolved_by:
                resolved_user = self.db.query(User).filter(User.id == case.resolved_by).first()
            
            # Prepare analysis details
            analysis_details = {
                "case": {
                    "id": case.id,
                    "case_id": case.case_id,
                    "status": case.status,
                    "priority": case.priority,
                    "flag_type": case.flag_type,
                    "risk_score": case.risk_score,
                    "risk_level": case.risk_level,
                    "reason_summary": case.reason_summary,
                    "detailed_explanation": case.detailed_explanation,
                    "suggested_actions": case.suggested_actions,
                    "review_notes": case.review_notes,
                    "resolution": case.resolution,
                    "created_at": case.created_at.isoformat() if case.created_at else None,
                    "updated_at": case.updated_at.isoformat() if case.updated_at else None,
                    "resolved_at": case.resolved_at.isoformat() if case.resolved_at else None
                },
                "transaction": {
                    "id": transaction.id if transaction else None,
                    "invoice_id": transaction.invoice_id if transaction else None,
                    "amount": float(transaction.amount) if transaction and transaction.amount else None,
                    "currency": transaction.currency if transaction else None,
                    "invoice_date": transaction.invoice_date.isoformat() if transaction and transaction.invoice_date else None,
                    "department": transaction.department if transaction else None,
                    "description": transaction.description if transaction else None
                },
                "vendor": {
                    "id": vendor.id if vendor else None,
                    "vendor_name": vendor.vendor_name if vendor else None,
                    "vendor_code": vendor.vendor_code if vendor else None
                },
                "assigned_to": {
                    "id": assigned_user.id if assigned_user else None,
                    "name": f"{assigned_user.first_name} {assigned_user.last_name}" if assigned_user else None,
                    "email": assigned_user.email if assigned_user else None
                } if assigned_user else None,
                "resolved_by": {
                    "id": resolved_user.id if resolved_user else None,
                    "name": f"{resolved_user.first_name} {resolved_user.last_name}" if resolved_user else None
                } if resolved_user else None,
                "analysis_metadata": case.analysis_metadata or {}
            }
            
            return analysis_details
            
        except Exception as e:
            logger.error(f"Failed to get case analysis details: {str(e)}")
            return None