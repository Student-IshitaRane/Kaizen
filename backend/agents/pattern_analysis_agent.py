import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import statistics
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from app.database.session import get_db
from models.purchase_ledger import PurchaseLedger
from models.vendor import Vendor
from .base_agent import BaseAgent, AgentRequest, AgentResponse
from core.config import settings

logger = logging.getLogger(__name__)

class PatternAnalysisAgent(BaseAgent):
    """Functional agent for analyzing transaction patterns and trends"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(
            name="pattern_analysis",
            description="Analyzes transaction patterns including vendor payment spikes, department spending, and temporal clustering"
        )
        self.required_context_fields = ["transaction_data", "db_session"]
        self.config = {
            "vendor_spike_score": 15,
            "department_spike_score": 12,
            "temporal_cluster_score": 10,
            "quarter_end_spike_score": 8,
            "concentration_risk_score": 20,
            "spike_threshold": 2.0,  # standard deviations
            "cluster_window_days": 7,
            "concentration_threshold": 0.3  # 30% of total spend
        }
        self.db = db_session
    
    def process(self, request: AgentRequest) -> AgentResponse:
        """Analyze transaction patterns"""
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
                from app.database.session import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            # Analyze all patterns
            patterns = []
            
            # 1. Vendor payment spikes
            vendor_spike = self._analyze_vendor_payment_spike(transaction_data)
            if vendor_spike:
                patterns.append(vendor_spike)
            
            # 2. Unusual department spending
            department_spike = self._analyze_department_spending(transaction_data)
            if department_spike:
                patterns.append(department_spike)
            
            # 3. Temporal clustering
            temporal_clusters = self._analyze_temporal_clustering(transaction_data)
            patterns.extend(temporal_clusters)
            
            # 4. Quarter-end spikes
            quarter_end_spike = self._analyze_quarter_end_spike(transaction_data)
            if quarter_end_spike:
                patterns.append(quarter_end_spike)
            
            # 5. Concentration risk
            concentration_risk = self._analyze_concentration_risk(transaction_data)
            if concentration_risk:
                patterns.append(concentration_risk)
            
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={
                    "status": "success",
                    "patterns_detected": len(patterns),
                    "patterns": patterns,
                    "summary": self._create_pattern_summary(patterns),
                    "metadata": {
                        "transaction_id": transaction_data.get("invoice_id"),
                        "vendor_id": transaction_data.get("vendor_id"),
                        "department": transaction_data.get("department")
                    }
                },
                confidence=0.85,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {str(e)}")
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={"error": str(e), "status": "failed"},
                confidence=0.0,
                processing_time_ms=processing_time_ms
            )
    
    def _analyze_vendor_payment_spike(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze vendor payment spikes compared to historical patterns"""
        vendor_id = transaction.get("vendor_id")
        amount = transaction.get("amount")
        invoice_date = transaction.get("invoice_date")
        
        if not all([vendor_id, amount, invoice_date]):
            return None
        
        try:
            trans_date = self._parse_date(invoice_date)
            if not trans_date:
                return None
            
            # Get vendor's historical monthly spending
            monthly_spending = self._get_vendor_monthly_spending(vendor_id)
            
            if len(monthly_spending) < 3:  # Need at least 3 months of data
                return None
            
            # Get current month
            current_month = trans_date.strftime("%Y-%m")
            current_month_spending = monthly_spending.get(current_month, 0)
            
            # Calculate statistics
            spending_values = list(monthly_spending.values())
            mean_spending = statistics.mean(spending_values)
            std_dev = statistics.stdev(spending_values) if len(spending_values) > 1 else 0
            
            # Check for spike
            if std_dev > 0:
                z_score = (current_month_spending - mean_spending) / std_dev
                if z_score > self.config["spike_threshold"]:
                    return {
                        "type": "vendor_payment_spike",
                        "severity": "medium",
                        "score": self.config["vendor_spike_score"],
                        "description": f"Vendor payment spike: ${current_month_spending:,.2f} in {current_month} (Z-score: {z_score:.2f})",
                        "evidence": {
                            "vendor_id": vendor_id,
                            "current_month": current_month,
                            "current_month_spending": current_month_spending,
                            "historical_mean": mean_spending,
                            "historical_std_dev": std_dev,
                            "z_score": z_score,
                            "months_analyzed": len(monthly_spending)
                        }
                    }
        
        except Exception as e:
            logger.warning(f"Vendor payment spike analysis failed: {e}")
        
        return None
    
    def _get_vendor_monthly_spending(self, vendor_id: str) -> Dict[str, float]:
        """Get vendor's monthly spending history"""
        monthly_spending = {}
        
        try:
            # Query vendor transactions grouped by month
            results = self.db.query(
                func.date_trunc('month', PurchaseLedger.invoice_date).label('month'),
                func.sum(PurchaseLedger.amount).label('total_amount')
            ).filter(
                PurchaseLedger.vendor_id == vendor_id,
                PurchaseLedger.amount.isnot(None)
            ).group_by(
                func.date_trunc('month', PurchaseLedger.invoice_date)
            ).order_by('month').all()
            
            for month, total_amount in results:
                if month and total_amount:
                    month_key = month.strftime("%Y-%m")
                    monthly_spending[month_key] = float(total_amount)
        
        except Exception as e:
            logger.warning(f"Failed to get vendor monthly spending: {e}")
        
        return monthly_spending
    
    def _analyze_department_spending(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze unusual department spending patterns"""
        department = transaction.get("department")
        amount = transaction.get("amount")
        invoice_date = transaction.get("invoice_date")
        
        if not all([department, amount, invoice_date]):
            return None
        
        try:
            trans_date = self._parse_date(invoice_date)
            if not trans_date:
                return None
            
            # Get department's historical monthly spending
            monthly_spending = self._get_department_monthly_spending(department)
            
            if len(monthly_spending) < 3:
                return None
            
            # Get current month
            current_month = trans_date.strftime("%Y-%m")
            current_month_spending = monthly_spending.get(current_month, 0)
            
            # Calculate statistics
            spending_values = list(monthly_spending.values())
            mean_spending = statistics.mean(spending_values)
            std_dev = statistics.stdev(spending_values) if len(spending_values) > 1 else 0
            
            # Check for unusual spending
            if std_dev > 0:
                z_score = (current_month_spending - mean_spending) / std_dev
                if abs(z_score) > self.config["spike_threshold"]:
                    direction = "above" if z_score > 0 else "below"
                    return {
                        "type": "unusual_department_spending",
                        "severity": "medium" if abs(z_score) > 3 else "low",
                        "score": self.config["department_spike_score"],
                        "description": f"Unusual department spending: {department} ${current_month_spending:,.2f} ({direction} average, Z-score: {z_score:.2f})",
                        "evidence": {
                            "department": department,
                            "current_month": current_month,
                            "current_month_spending": current_month_spending,
                            "historical_mean": mean_spending,
                            "historical_std_dev": std_dev,
                            "z_score": z_score,
                            "direction": direction,
                            "months_analyzed": len(monthly_spending)
                        }
                    }
        
        except Exception as e:
            logger.warning(f"Department spending analysis failed: {e}")
        
        return None
    
    def _get_department_monthly_spending(self, department: str) -> Dict[str, float]:
        """Get department's monthly spending history"""
        monthly_spending = {}
        
        try:
            results = self.db.query(
                func.date_trunc('month', PurchaseLedger.invoice_date).label('month'),
                func.sum(PurchaseLedger.amount).label('total_amount')
            ).filter(
                PurchaseLedger.department == department,
                PurchaseLedger.amount.isnot(None)
            ).group_by(
                func.date_trunc('month', PurchaseLedger.invoice_date)
            ).order_by('month').all()
            
            for month, total_amount in results:
                if month and total_amount:
                    month_key = month.strftime("%Y-%m")
                    monthly_spending[month_key] = float(total_amount)
        
        except Exception as e:
            logger.warning(f"Failed to get department monthly spending: {e}")
        
        return monthly_spending
    def _analyze_temporal_clustering(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze temporal clustering of transactions"""
        patterns = []
        vendor_id = transaction.get("vendor_id")
        department = transaction.get("department")
        invoice_date = transaction.get("invoice_date")
        
        if not invoice_date:
            return patterns
        
        try:
            trans_date = self._parse_date(invoice_date)
            if not trans_date:
                return patterns
            
            # Calculate time window
            window_days = self.config["cluster_window_days"]
            start_date = trans_date - timedelta(days=window_days)
            
            # Check vendor-based clustering
            if vendor_id:
                vendor_cluster = self._analyze_vendor_temporal_cluster(vendor_id, trans_date, start_date)
                if vendor_cluster:
                    patterns.append(vendor_cluster)
            
            # Check department-based clustering
            if department:
                department_cluster = self._analyze_department_temporal_cluster(department, trans_date, start_date)
                if department_cluster:
                    patterns.append(department_cluster)
        
        except Exception as e:
            logger.warning(f"Temporal clustering analysis failed: {e}")
        
        return patterns
    
    def _analyze_vendor_temporal_cluster(self, vendor_id: str, trans_date: datetime, start_date: datetime) -> Optional[Dict[str, Any]]:
        """Analyze temporal clustering for a specific vendor"""
        try:
            # Count vendor transactions in time window
            cluster_count = self.db.query(PurchaseLedger).filter(
                PurchaseLedger.vendor_id == vendor_id,
                PurchaseLedger.invoice_date.between(start_date, trans_date)
            ).count()
            
            if cluster_count >= 5:  # 5 or more transactions in window
                return {
                    "type": "vendor_temporal_cluster",
                    "severity": "medium",
                    "score": self.config["temporal_cluster_score"],
                    "description": f"Vendor temporal clustering: {cluster_count} transactions in {self.config['cluster_window_days']} days",
                    "evidence": {
                        "vendor_id": vendor_id,
                        "cluster_count": cluster_count,
                        "time_window_days": self.config["cluster_window_days"],
                        "window_start": start_date.isoformat(),
                        "window_end": trans_date.isoformat()
                    }
                }
        
        except Exception as e:
            logger.warning(f"Vendor temporal cluster analysis failed: {e}")
        
        return None
    
    def _analyze_department_temporal_cluster(self, department: str, trans_date: datetime, start_date: datetime) -> Optional[Dict[str, Any]]:
        """Analyze temporal clustering for a specific department"""
        try:
            # Count department transactions in time window
            cluster_count = self.db.query(PurchaseLedger).filter(
                PurchaseLedger.department == department,
                PurchaseLedger.invoice_date.between(start_date, trans_date)
            ).count()
            
            if cluster_count >= 8:  # 8 or more transactions in window
                return {
                    "type": "department_temporal_cluster",
                    "severity": "medium",
                    "score": self.config["temporal_cluster_score"],
                    "description": f"Department temporal clustering: {cluster_count} transactions in {self.config['cluster_window_days']} days",
                    "evidence": {
                        "department": department,
                        "cluster_count": cluster_count,
                        "time_window_days": self.config["cluster_window_days"],
                        "window_start": start_date.isoformat(),
                        "window_end": trans_date.isoformat()
                    }
                }
        
        except Exception as e:
            logger.warning(f"Department temporal cluster analysis failed: {e}")
        
        return None
    
    def _analyze_quarter_end_spike(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze quarter-end transaction spikes"""
        invoice_date = transaction.get("invoice_date")
        
        if not invoice_date:
            return None
        
        try:
            trans_date = self._parse_date(invoice_date)
            if not trans_date:
                return None
            
            # Check if transaction is in last week of quarter
            quarter_end = self._is_quarter_end_week(trans_date)
            if not quarter_end:
                return None
            
            # Get quarter-end spending pattern
            quarter_end_spending = self._get_quarter_end_spending_pattern(trans_date)
            
            if quarter_end_spending.get("is_spike", False):
                return {
                    "type": "quarter_end_spike",
                    "severity": "low",
                    "score": self.config["quarter_end_spike_score"],
                    "description": f"Quarter-end transaction spike detected",
                    "evidence": {
                        "transaction_date": trans_date.isoformat(),
                        "quarter": f"Q{quarter_end_spending['quarter']} {trans_date.year}",
                        "quarter_end_week_spending": quarter_end_spending.get("week_spending", 0),
                        "quarter_average_weekly": quarter_end_spending.get("quarter_avg_weekly", 0),
                        "spike_ratio": quarter_end_spending.get("spike_ratio", 0)
                    }
                }
        
        except Exception as e:
            logger.warning(f"Quarter-end spike analysis failed: {e}")
        
        return None
    
    def _is_quarter_end_week(self, date_obj: datetime) -> bool:
        """Check if date is in last week of quarter"""
        # Get quarter end month
        quarter = (date_obj.month - 1) // 3 + 1
        quarter_end_month = quarter * 3
        
        # Check if date is in last 7 days of quarter end month
        if date_obj.month == quarter_end_month:
            # Get last day of month
            if date_obj.month == 12:
                last_day = 31
            else:
                next_month = datetime(date_obj.year, date_obj.month + 1, 1)
                last_day = (next_month - timedelta(days=1)).day
            
            return date_obj.day > (last_day - 7)
        
        return False
    
    def _get_quarter_end_spending_pattern(self, trans_date: datetime) -> Dict[str, Any]:
        """Get quarter-end spending pattern analysis"""
        try:
            # Determine quarter
            quarter = (trans_date.month - 1) // 3 + 1
            quarter_start_month = (quarter - 1) * 3 + 1
            quarter_end_month = quarter * 3
            
            # Get quarter start and end dates
            quarter_start = datetime(trans_date.year, quarter_start_month, 1)
            if quarter_end_month == 12:
                quarter_end = datetime(trans_date.year, 12, 31)
            else:
                quarter_end = datetime(trans_date.year, quarter_end_month + 1, 1) - timedelta(days=1)
            
            # Get total spending in quarter
            quarter_total = self.db.query(func.sum(PurchaseLedger.amount)).filter(
                PurchaseLedger.invoice_date.between(quarter_start, quarter_end)
            ).scalar() or 0
            
            # Get spending in last week of quarter
            last_week_start = quarter_end - timedelta(days=7)
            last_week_spending = self.db.query(func.sum(PurchaseLedger.amount)).filter(
                PurchaseLedger.invoice_date.between(last_week_start, quarter_end)
            ).scalar() or 0
            
            # Calculate weekly average
            weeks_in_quarter = 13  # Approximate
            quarter_avg_weekly = float(quarter_total) / weeks_in_quarter if weeks_in_quarter > 0 else 0
            
            # Check for spike
            spike_ratio = float(last_week_spending) / quarter_avg_weekly if quarter_avg_weekly > 0 else 0
            
            return {
                "quarter": quarter,
                "quarter_total": float(quarter_total),
                "week_spending": float(last_week_spending),
                "quarter_avg_weekly": quarter_avg_weekly,
                "spike_ratio": spike_ratio,
                "is_spike": spike_ratio > 2.0  # More than 2x weekly average
            }
        
        except Exception as e:
            logger.warning(f"Failed to get quarter-end spending pattern: {e}")
            return {"is_spike": False}
    
    def _analyze_concentration_risk(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze vendor concentration risk"""
        vendor_id = transaction.get("vendor_id")
        
        if not vendor_id:
            return None
        
        try:
            # Get total spending and vendor spending
            total_spending_result = self.db.query(func.sum(PurchaseLedger.amount)).scalar() or 0
            vendor_spending_result = self.db.query(func.sum(PurchaseLedger.amount)).filter(
                PurchaseLedger.vendor_id == vendor_id
            ).scalar() or 0
            
            total_spending = float(total_spending_result)
            vendor_spending = float(vendor_spending_result)
            
            if total_spending > 0:
                concentration_ratio = vendor_spending / total_spending
                threshold = self.config["concentration_threshold"]
                
                if concentration_ratio > threshold:
                    return {
                        "type": "vendor_concentration_risk",
                        "severity": "high",
                        "score": self.config["concentration_risk_score"],
                        "description": f"Vendor concentration risk: {vendor_id} accounts for {concentration_ratio:.1%} of total spend",
                        "evidence": {
                            "vendor_id": vendor_id,
                            "vendor_spending": vendor_spending,
                            "total_spending": total_spending,
                            "concentration_ratio": concentration_ratio,
                            "threshold": threshold,
                            "exceeds_threshold": True
                        }
                    }
        
        except Exception as e:
            logger.warning(f"Concentration risk analysis failed: {e}")
        
        return None
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date from various formats"""
        if isinstance(date_value, datetime):
            return date_value
        elif isinstance(date_value, date):
            return datetime.combine(date_value, datetime.min.time())
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
    
    def _create_pattern_summary(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of detected patterns"""
        if not patterns:
            return {
                "total_patterns": 0,
                "high_severity_count": 0,
                "medium_severity_count": 0,
                "low_severity_count": 0,
                "total_score": 0
            }
        
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        total_score = 0
        
        for pattern in patterns:
            severity = pattern.get("severity", "low")
            score = pattern.get("score", 0)
            
            if severity in severity_counts:
                severity_counts[severity] += 1
            total_score += score
        
        return {
            "total_patterns": len(patterns),
            "high_severity_count": severity_counts["high"],
            "medium_severity_count": severity_counts["medium"],
            "low_severity_count": severity_counts["low"],
            "total_score": total_score,
            "pattern_types": list(set(p.get("type", "unknown") for p in patterns))
        }