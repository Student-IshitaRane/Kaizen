from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import date, datetime
from decimal import Decimal
import uuid
import logging
import asyncio
from models.purchase_ledger import PurchaseLedger
from models.vendor import Vendor
from models.user import User
from streaming.kafka_producer import producer
from services.agent_orchestrator import AgentOrchestrator
from services.analysis_result_service import AnalysisResultService
from websocket.manager import websocket_manager
from core.config import settings

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.kafka_producer = producer
        self.agent_orchestrator = AgentOrchestrator(db)
        self.analysis_result_service = AnalysisResultService(db)
    
    def create_purchase_transaction(
        self,
        invoice_id: str,
        vendor_id: str,
        amount: Decimal,
        invoice_date: date,
        created_by: str,
        department: Optional[str] = None,
        approver_id: Optional[str] = None,
        description: Optional[str] = None,
        currency: str = "USD",
        posting_date: Optional[date] = None,
        cost_center: Optional[str] = None,
        gl_account: Optional[str] = None,
        approval_date: Optional[date] = None,
        reference_number: Optional[str] = None,
        po_number: Optional[str] = None,
        payment_method: Optional[str] = None,
        bank_account: Optional[str] = None
    ) -> PurchaseLedger:
        """Create a new purchase transaction"""
        
        # Verify vendor exists
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise ValueError(f"Vendor not found: {vendor_id}")
        
        # Verify approver exists if provided
        if approver_id:
            approver = self.db.query(User).filter(User.id == approver_id).first()
            if not approver:
                raise ValueError(f"Approver not found: {approver_id}")
        
        # Check for duplicate invoice
        existing = self.db.query(PurchaseLedger).filter(
            PurchaseLedger.invoice_id == invoice_id
        ).first()
        
        if existing:
            raise ValueError(f"Invoice already exists: {invoice_id}")
        
        # Create transaction
        transaction = PurchaseLedger(
            id=uuid.uuid4(),
            invoice_id=invoice_id,
            vendor_id=uuid.UUID(vendor_id),
            amount=amount,
            invoice_date=invoice_date,
            department=department,
            approver_id=uuid.UUID(approver_id) if approver_id else None,
            description=description,
            currency=currency,
            posting_date=posting_date,
            cost_center=cost_center,
            gl_account=gl_account,
            approval_date=approval_date,
            reference_number=reference_number,
            po_number=po_number,
            payment_method=payment_method,
            bank_account=bank_account,
            status="submitted"
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        # Publish to Kafka for real-time analysis
        self._publish_to_kafka(transaction)
        
        # Send WebSocket event for transaction processed
        self._send_transaction_processed_event(transaction)
        
        # Run immediate analysis if enabled
        analysis_summary = self._run_immediate_analysis(transaction)
        
        # Add analysis summary to transaction response
        transaction.analysis_summary = analysis_summary
        
        return transaction
    
    def get_transactions(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        vendor_id: Optional[str] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        department: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get transactions with filtering and pagination"""
        
        query = self.db.query(PurchaseLedger)
        
        if user_id:
            # For finance users, only show their transactions
            query = query.filter(PurchaseLedger.approver_id == user_id)
        
        if start_date:
            query = query.filter(PurchaseLedger.invoice_date >= start_date)
        if end_date:
            query = query.filter(PurchaseLedger.invoice_date <= end_date)
        if vendor_id:
            query = query.filter(PurchaseLedger.vendor_id == vendor_id)
        if min_amount:
            query = query.filter(PurchaseLedger.amount >= min_amount)
        if max_amount:
            query = query.filter(PurchaseLedger.amount <= max_amount)
        if department:
            query = query.filter(PurchaseLedger.department == department)
        
        total = query.count()
        
        transactions = query.order_by(desc(PurchaseLedger.created_at)) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()
        
        return {
            "transactions": transactions,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[PurchaseLedger]:
        """Get transaction by ID"""
        return self.db.query(PurchaseLedger).filter(PurchaseLedger.id == transaction_id).first()
    
    def get_vendor_transaction_summary(self, vendor_id: str) -> Dict[str, Any]:
        """Get transaction summary for a vendor"""
        
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise ValueError(f"Vendor not found: {vendor_id}")
        
        transactions = self.db.query(PurchaseLedger).filter(
            PurchaseLedger.vendor_id == vendor_id
        ).all()
        
        total_transactions = len(transactions)
        total_amount = sum(t.amount for t in transactions)
        
        # Get recent transactions
        recent_transactions = self.db.query(PurchaseLedger).filter(
            PurchaseLedger.vendor_id == vendor_id
        ).order_by(desc(PurchaseLedger.invoice_date)).limit(10).all()
        
        # Get monthly trend
        monthly_trend = {}
        for transaction in transactions:
            month_key = transaction.invoice_date.strftime("%Y-%m")
            if month_key not in monthly_trend:
                monthly_trend[month_key] = {"count": 0, "amount": Decimal('0')}
            monthly_trend[month_key]["count"] += 1
            monthly_trend[month_key]["amount"] += transaction.amount
        
        return {
            "vendor": {
                "id": str(vendor.id),
                "vendor_code": vendor.vendor_code,
                "vendor_name": vendor.vendor_name
            },
            "summary": {
                "total_transactions": total_transactions,
                "total_amount": float(total_amount),
                "average_amount": float(total_amount / total_transactions) if total_transactions > 0 else 0
            },
            "recent_transactions": recent_transactions,
            "monthly_trend": monthly_trend
        }
    
    def _publish_to_kafka(self, transaction: PurchaseLedger):
        """Publish transaction to Kafka for real-time analysis"""
        try:
            # Prepare transaction data for Kafka
            transaction_data = {
                "transaction_id": str(transaction.id),
                "invoice_id": transaction.invoice_id,
                "vendor_id": str(transaction.vendor_id),
                "amount": float(transaction.amount),
                "invoice_date": transaction.invoice_date.isoformat() if transaction.invoice_date else None,
                "department": transaction.department,
                "description": transaction.description,
                "currency": transaction.currency,
                "status": transaction.status,
                "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                "metadata": {
                    "transaction_type": "purchase",
                    "source": "transaction_service"
                }
            }
            
            # Publish to Kafka
            self.kafka_producer.publish_transaction_created(transaction_data)
            logger.info(f"Published transaction {transaction.invoice_id} to Kafka")
            
        except Exception as e:
            logger.error(f"Failed to publish transaction to Kafka: {e}")
            # Don't fail the transaction creation if Kafka publishing fails
            # The transaction is already saved to the database
    
    def _run_immediate_analysis(self, transaction: PurchaseLedger) -> Optional[Dict[str, Any]]:
        """Run immediate analysis on transaction"""
        try:
            # Prepare transaction data for analysis
            transaction_data = {
                "invoice_id": transaction.invoice_id,
                "vendor_id": str(transaction.vendor_id),
                "amount": float(transaction.amount) if transaction.amount else None,
                "currency": transaction.currency,
                "invoice_date": transaction.invoice_date.isoformat() if transaction.invoice_date else None,
                "posting_date": transaction.posting_date.isoformat() if transaction.posting_date else None,
                "department": transaction.department,
                "description": transaction.description,
                "approver_id": str(transaction.approver_id) if transaction.approver_id else None,
                "cost_center": transaction.cost_center,
                "gl_account": transaction.gl_account,
                "reference_number": transaction.reference_number,
                "po_number": transaction.po_number,
                "payment_method": transaction.payment_method,
                "bank_account": transaction.bank_account,
                "status": transaction.status
            }
            
            # Execute analysis pipeline
            pipeline_results = self.agent_orchestrator.execute_pipeline(
                transaction_data=transaction_data,
                pipeline_name="default_pipeline",
                immediate_analysis=settings.ENABLE_IMMEDIATE_ANALYSIS
            )
            
            # Check if analysis was performed
            if pipeline_results.get("status") == "skipped":
                logger.info(f"Immediate analysis skipped for transaction {transaction.invoice_id}")
                return None
            
            # Create flagged case if needed
            analysis_results = pipeline_results.get("analysis_results", {})
            
            flagged_case = self.analysis_result_service.create_flagged_case_from_analysis(
                transaction_data=transaction_data,
                analysis_results=analysis_results,
                pipeline_results=pipeline_results
            )
            
            # Prepare analysis summary
            analysis_summary = {
                "pipeline_status": pipeline_results.get("overall_status"),
                "processing_time_ms": pipeline_results.get("processing_time_ms", 0),
                "analysis_summary": pipeline_results.get("analysis_summary", {}),
                "flagged_case_created": flagged_case is not None,
                "flagged_case_id": flagged_case.id if flagged_case else None,
                "risk_score": analysis_results.get("risk_scoring", {}).get("overall_risk_score", 0),
                "risk_level": analysis_results.get("risk_scoring", {}).get("risk_level", "unknown")
            }
            
            logger.info(f"Immediate analysis completed for transaction {transaction.invoice_id}")
            
            # Send WebSocket event for analysis completion
            self._send_analysis_completed_event(transaction, analysis_summary)
            
            # Send WebSocket event for case creation if flagged
            if flagged_case:
                case_data = {
                    "case_id": flagged_case.id,
                    "transaction_id": str(transaction.id),
                    "flag_type": flagged_case.flag_type,
                    "risk_score": analysis_summary.get("risk_score", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
                self._send_case_created_event(case_data)
            
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Failed to run immediate analysis: {str(e)}")
            return None
    
    def _send_transaction_processed_event(self, transaction: PurchaseLedger):
        """Send WebSocket event for processed transaction"""
        try:
            transaction_data = {
                "transaction_id": str(transaction.id),
                "invoice_id": transaction.invoice_id,
                "vendor_id": str(transaction.vendor_id),
                "amount": float(transaction.amount) if transaction.amount else 0,
                "currency": transaction.currency,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Run in background to not block the main thread
            asyncio.create_task(
                websocket_manager.send_transaction_processed(transaction_data)
            )
            logger.info(f"Sent WebSocket event for transaction: {transaction.invoice_id}")
        except Exception as e:
            logger.error(f"Failed to send WebSocket event: {e}")
    
    def _send_analysis_completed_event(self, transaction: PurchaseLedger, analysis_summary: Dict[str, Any]):
        """Send WebSocket event for analysis completion"""
        try:
            analysis_data = {
                "transaction_id": str(transaction.id),
                "invoice_id": transaction.invoice_id,
                "risk_score": analysis_summary.get("risk_score", 0),
                "risk_level": analysis_summary.get("risk_level", "unknown"),
                "processing_time_ms": analysis_summary.get("processing_time_ms", 0),
                "flagged_case_created": analysis_summary.get("flagged_case_created", False),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Run in background
            asyncio.create_task(
                websocket_manager.send_analysis_completed(analysis_data)
            )
            logger.info(f"Sent analysis completed event for transaction: {transaction.invoice_id}")
        except Exception as e:
            logger.error(f"Failed to send analysis WebSocket event: {e}")
    
    def _send_case_created_event(self, case_data: Dict[str, Any]):
        """Send WebSocket event for case creation"""
        try:
            asyncio.create_task(
                websocket_manager.send_case_created(case_data)
            )
            logger.info(f"Sent case created event: {case_data.get('case_id')}")
        except Exception as e:
            logger.error(f"Failed to send case created event: {e}")