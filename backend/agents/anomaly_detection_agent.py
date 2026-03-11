import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import statistics
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.database.session import get_db
from models.purchase_ledger import PurchaseLedger
from models.vendor import Vendor
from .base_agent import BaseAgent, AgentRequest, AgentResponse
from core.config import settings

logger = logging.getLogger(__name__)

class AnomalyDetectionAgent(BaseAgent):
    """Functional agent for detecting anomalies using rule-based and analytics checks"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(
            name="anomaly_detection",
            description="Detects anomalies including duplicates, unusual amounts, timing issues, and threshold avoidance"
        )
        self.required_context_fields = ["transaction_data", "db_session"]
        self.config = {
            "exact_duplicate_score": 40,
            "near_duplicate_score": 30,
            "unusual_amount_score": 20,
            "round_number_score": 15,
            "weekend_posting_score": 10,
            "rapid_repeat_score": 15,
            "threshold_avoidance_score": 25,
            "dormant_vendor_score": 15,
            "round_number_threshold": 1000.0,
            "unusual_amount_threshold": 2.0,  # standard deviations
            "rapid_repeat_hours": settings.RAPID_REPEAT_WINDOW_HOURS,
            "dormant_vendor_days": settings.DORMANT_VENDOR_DAYS,
            "approval_threshold": settings.APPROVAL_THRESHOLD_DEFAULT,
            "near_duplicate_days": settings.NEAR_DUPLICATE_DATE_WINDOW_DAYS
        }
        self.db = db_session
    
    def process(self, request: AgentRequest) -> AgentResponse:
        """Detect anomalies in transaction data"""
        start_time = datetime.utcnow()
        
        if not self.validate_request(request):
            return self.create_response(
                result={"error": "Missing required context fields"},
                confidence=0.0,
                processing_time_ms=0
            )
        
        try:
            transaction_data = request.transaction_data
            self.db = request.context.get("db_session", self.db)
            
            if not self.db:
                # Create a new session if none provided
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            # Detect all anomalies
            anomalies = []
            
            # 1. Exact duplicate invoice detection
            exact_duplicate = self._detect_exact_duplicate(transaction_data)
            if exact_duplicate:
                anomalies.append(exact_duplicate)
            
            # 2. Near-duplicate invoice detection
            near_duplicates = self._detect_near_duplicates(transaction_data)
            anomalies.extend(near_duplicates)
            
            # 3. Unusual transaction amount
            unusual_amount = self._detect_unusual_amount(transaction_data)
            if unusual_amount:
                anomalies.append(unusual_amount)
            
            # 4. Round-number transaction detection
            round_number = self._detect_round_number(transaction_data)
            if round_number:
                anomalies.append(round_number)
            
            # 5. Weekend/holiday posting detection
            weekend_posting = self._detect_weekend_posting(transaction_data)
            if weekend_posting:
                anomalies.append(weekend_posting)
            
            # 6. Rapid repeated payments
            rapid_repeat = self._detect_rapid_repeat(transaction_data)
            if rapid_repeat:
                anomalies.append(rapid_repeat)
            
            # 7. Threshold avoidance pattern
            threshold_avoidance = self._detect_threshold_avoidance(transaction_data)
            if threshold_avoidance:
                anomalies.append(threshold_avoidance)
            
            # 8. Dormant vendor activity
            dormant_vendor = self._detect_dormant_vendor(transaction_data)
            if dormant_vendor:
                anomalies.append(dormant_vendor)
            
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={
                    "status": "success",
                    "anomalies_detected": len(anomalies),
                    "anomalies": anomalies,
                    "summary": self._create_anomaly_summary(anomalies),
                    "metadata": {
                        "transaction_id": transaction_data.get("invoice_id"),
                        "vendor_id": transaction_data.get("vendor_id"),
                        "detection_methods_used": list(self.config.keys())[:8]
                    }
                },
                confidence=0.90,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={"error": str(e), "status": "failed"},
                confidence=0.0,
                processing_time_ms=processing_time_ms
            )
    
    def _detect_exact_duplicate(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect exact duplicate invoice"""
        invoice_id = transaction.get("invoice_id")
        vendor_id = transaction.get("vendor_id")
        
        if not invoice_id or not vendor_id:
            return None
        
        try:
            # Query for exact duplicate
            duplicate = self.db.query(PurchaseLedger).filter(
                PurchaseLedger.invoice_id == invoice_id,
                PurchaseLedger.vendor_id == vendor_id
            ).first()
            
            if duplicate:
                return {
                    "type": "exact_duplicate_invoice",
                    "severity": "high",
                    "score": self.config["exact_duplicate_score"],
                    "description": f"Exact duplicate invoice detected: {invoice_id} for vendor {vendor_id}",
                    "evidence": {
                        "existing_invoice_id": duplicate.invoice_id,
                        "existing_amount": float(duplicate.amount) if duplicate.amount else None,
                        "existing_date": duplicate.invoice_date.isoformat() if duplicate.invoice_date else None
                    }
                }
        except Exception as e:
            logger.warning(f"Exact duplicate detection failed: {e}")
        
        return None
    
    def _detect_near_duplicates(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect near-duplicate invoices"""
        anomalies = []
        invoice_id = transaction.get("invoice_id")
        vendor_id = transaction.get("vendor_id")
        amount = transaction.get("amount")
        invoice_date = transaction.get("invoice_date")
        
        if not all([invoice_id, vendor_id, amount, invoice_date]):
            return anomalies
        
        try:
            # Parse date
            trans_date = self._parse_date(invoice_date)
            if not trans_date:
                return anomalies
            
            # Calculate date window
            start_date = trans_date - timedelta(days=self.config["near_duplicate_days"])
            end_date = trans_date + timedelta(days=self.config["near_duplicate_days"])
            
            # Find similar transactions
            similar_transactions = self.db.query(PurchaseLedger).filter(
                PurchaseLedger.vendor_id == vendor_id,
                PurchaseLedger.invoice_date.between(start_date, end_date),
                PurchaseLedger.amount.between(float(amount) * 0.95, float(amount) * 1.05),  # ±5% amount
                PurchaseLedger.invoice_id != invoice_id  # Exclude self
            ).all()
            
            for similar in similar_transactions:
                # Check invoice ID similarity (simple string similarity)
                similarity = self._calculate_string_similarity(invoice_id, similar.invoice_id)
                if similarity > 0.7:  # 70% similarity threshold
                    anomalies.append({
                        "type": "near_duplicate_invoice",
                        "severity": "medium",
                        "score": self.config["near_duplicate_score"],
                        "description": f"Near-duplicate invoice detected: {invoice_id} similar to {similar.invoice_id}",
                        "evidence": {
                            "similar_invoice_id": similar.invoice_id,
                            "similarity_score": similarity,
                            "similar_amount": float(similar.amount) if similar.amount else None,
                            "similar_date": similar.invoice_date.isoformat() if similar.invoice_date else None,
                            "date_difference_days": (trans_date - similar.invoice_date.date()).days if similar.invoice_date else None,
                            "amount_difference_percent": abs(float(amount) - float(similar.amount)) / float(amount) * 100 if similar.amount else None
                        }
                    })
        
        except Exception as e:
            logger.warning(f"Near duplicate detection failed: {e}")
        
        return anomalies
    
    def _detect_unusual_amount(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect unusual transaction amount compared to vendor history"""
        vendor_id = transaction.get("vendor_id")
        amount = transaction.get("amount")
        
        if not vendor_id or not amount:
            return None
        
        try:
            # Get vendor's historical transactions
            vendor_transactions = self.db.query(PurchaseLedger).filter(
                PurchaseLedger.vendor_id == vendor_id
            ).all()
            
            if len(vendor_transactions) < 5:  # Need enough data
                return None
            
            # Calculate statistics
            amounts = [float(t.amount) for t in vendor_transactions if t.amount]
            if not amounts:
                return None
            
            mean_amount = statistics.mean(amounts)
            std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # Check if current amount is unusual
            if std_dev > 0:
                z_score = abs(float(amount) - mean_amount) / std_dev
                if z_score > self.config["unusual_amount_threshold"]:
                    return {
                        "type": "unusual_transaction_amount",
                        "severity": "medium",
                        "score": self.config["unusual_amount_score"],
                        "description": f"Unusual transaction amount: ${float(amount):,.2f} (Z-score: {z_score:.2f})",
                        "evidence": {
                            "current_amount": float(amount),
                            "vendor_mean": mean_amount,
                            "vendor_std_dev": std_dev,
                            "z_score": z_score,
                            "historical_count": len(vendor_transactions)
                        }
                    }
        
        except Exception as e:
            logger.warning(f"Unusual amount detection failed: {e}")
        
        return None
    def _detect_round_number(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect round-number transaction amounts"""
        amount = transaction.get("amount")
        
        if not amount:
            return None
        
        try:
            amount_float = float(amount)
            threshold = self.config["round_number_threshold"]
            
            # Check for exact round numbers (divisible by threshold)
            if amount_float >= threshold and amount_float % threshold == 0:
                return {
                    "type": "round_number_amount",
                    "severity": "low",
                    "score": self.config["round_number_score"],
                    "description": f"Round number transaction: ${amount_float:,.2f} (divisible by ${threshold:,.2f})",
                    "evidence": {
                        "amount": amount_float,
                        "threshold": threshold,
                        "multiple": amount_float / threshold
                    }
                }
            
            # Check for common round numbers (100, 1000, 10000, etc.)
            common_rounds = [100, 500, 1000, 5000, 10000, 50000, 100000]
            for round_num in common_rounds:
                if amount_float == round_num:
                    return {
                        "type": "common_round_number",
                        "severity": "low",
                        "score": self.config["round_number_score"],
                        "description": f"Common round number: ${amount_float:,.2f}",
                        "evidence": {
                            "amount": amount_float,
                            "round_type": f"${round_num:,.2f}"
                        }
                    }
        
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _detect_weekend_posting(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect weekend or holiday posting"""
        invoice_date = transaction.get("invoice_date")
        
        if not invoice_date:
            return None
        
        try:
            trans_date = self._parse_date(invoice_date)
            if not trans_date:
                return None
            
            # Check if weekend (Saturday=5, Sunday=6)
            if trans_date.weekday() >= 5:
                return {
                    "type": "weekend_posting",
                    "severity": "low",
                    "score": self.config["weekend_posting_score"],
                    "description": f"Weekend transaction: {trans_date.strftime('%A, %Y-%m-%d')}",
                    "evidence": {
                        "transaction_date": trans_date.isoformat(),
                        "day_of_week": trans_date.strftime('%A'),
                        "is_weekend": True
                    }
                }
            
            # TODO: Add holiday detection
            # Could integrate with holiday calendar API or local holiday list
        
        except Exception as e:
            logger.warning(f"Weekend posting detection failed: {e}")
        
        return None
    
    def _detect_rapid_repeat(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect rapid repeated payments to same vendor"""
        vendor_id = transaction.get("vendor_id")
        invoice_date = transaction.get("invoice_date")
        
        if not vendor_id or not invoice_date:
            return None
        
        try:
            trans_date = self._parse_date(invoice_date)
            if not trans_date:
                return None
            
            # Calculate time window
            window_hours = self.config["rapid_repeat_hours"]
            start_date = trans_date - timedelta(hours=window_hours)
            
            # Count transactions in time window
            recent_count = self.db.query(PurchaseLedger).filter(
                PurchaseLedger.vendor_id == vendor_id,
                PurchaseLedger.invoice_date >= start_date,
                PurchaseLedger.invoice_date <= trans_date
            ).count()
            
            if recent_count >= 3:  # 3 or more transactions in window
                return {
                    "type": "rapid_repeat_payment",
                    "severity": "medium",
                    "score": self.config["rapid_repeat_score"],
                    "description": f"Rapid repeat payments: {recent_count} transactions in {window_hours} hours",
                    "evidence": {
                        "vendor_id": vendor_id,
                        "time_window_hours": window_hours,
                        "transaction_count": recent_count,
                        "window_start": start_date.isoformat(),
                        "window_end": trans_date.isoformat()
                    }
                }
        
        except Exception as e:
            logger.warning(f"Rapid repeat detection failed: {e}")
        
        return None
    
    def _detect_threshold_avoidance(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect threshold avoidance patterns"""
        amount = transaction.get("amount")
        
        if not amount:
            return None
        
        try:
            amount_float = float(amount)
            threshold = self.config["approval_threshold"]
            
            # Check if amount is just below approval threshold
            if threshold * 0.95 <= amount_float < threshold:  # Within 5% below threshold
                return {
                    "type": "threshold_avoidance",
                    "severity": "medium",
                    "score": self.config["threshold_avoidance_score"],
                    "description": f"Threshold avoidance: ${amount_float:,.2f} (just below ${threshold:,.2f} approval limit)",
                    "evidence": {
                        "amount": amount_float,
                        "approval_threshold": threshold,
                        "difference": threshold - amount_float,
                        "percentage_below": (threshold - amount_float) / threshold * 100
                    }
                }
        
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _detect_dormant_vendor(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect dormant vendor activity"""
        vendor_id = transaction.get("vendor_id")
        invoice_date = transaction.get("invoice_date")
        
        if not vendor_id or not invoice_date:
            return None
        
        try:
            trans_date = self._parse_date(invoice_date)
            if not trans_date:
                return None
            
            # Find vendor's last transaction before current one
            last_transaction = self.db.query(PurchaseLedger).filter(
                PurchaseLedger.vendor_id == vendor_id,
                PurchaseLedger.invoice_date < trans_date
            ).order_by(PurchaseLedger.invoice_date.desc()).first()
            
            if last_transaction and last_transaction.invoice_date:
                days_inactive = (trans_date - last_transaction.invoice_date.date()).days
                dormant_threshold = self.config["dormant_vendor_days"]
                
                if days_inactive > dormant_threshold:
                    return {
                        "type": "dormant_vendor_activity",
                        "severity": "medium",
                        "score": self.config["dormant_vendor_score"],
                        "description": f"Dormant vendor reactivated: {days_inactive} days since last transaction",
                        "evidence": {
                            "vendor_id": vendor_id,
                            "days_inactive": days_inactive,
                            "dormant_threshold": dormant_threshold,
                            "last_transaction_date": last_transaction.invoice_date.isoformat(),
                            "current_transaction_date": trans_date.isoformat()
                        }
                    }
        
        except Exception as e:
            logger.warning(f"Dormant vendor detection failed: {e}")
        
        return None
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date from various formats"""
        if isinstance(date_value, datetime):
            return date_value
        elif isinstance(date_value, date):
            return datetime.combine(date_value, datetime.min.time())
        elif isinstance(date_value, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError:
                # Try common formats
                formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"]
                for fmt in formats:
                    try:
                        return datetime.strptime(date_value, fmt)
                    except ValueError:
                        continue
        return None
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity (0-1)"""
        if not str1 or not str2:
            return 0.0
        
        # Convert to lowercase and remove non-alphanumeric
        s1 = re.sub(r'[^a-z0-9]', '', str1.lower())
        s2 = re.sub(r'[^a-z0-9]', '', str2.lower())
        
        if not s1 or not s2:
            return 0.0
        
        # Calculate Jaccard similarity of character sets
        set1 = set(s1)
        set2 = set(s2)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _create_anomaly_summary(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of detected anomalies"""
        if not anomalies:
            return {
                "total_anomalies": 0,
                "high_severity_count": 0,
                "medium_severity_count": 0,
                "low_severity_count": 0,
                "total_score": 0
            }
        
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        total_score = 0
        
        for anomaly in anomalies:
            severity = anomaly.get("severity", "low")
            score = anomaly.get("score", 0)
            
            if severity in severity_counts:
                severity_counts[severity] += 1
            total_score += score
        
        return {
            "total_anomalies": len(anomalies),
            "high_severity_count": severity_counts["high"],
            "medium_severity_count": severity_counts["medium"],
            "low_severity_count": severity_counts["low"],
            "total_score": total_score,
            "anomaly_types": list(set(a.get("type", "unknown") for a in anomalies))
        }