import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentRequest, AgentResponse
from core.config import settings

logger = logging.getLogger(__name__)

class RiskScoringAgent(BaseAgent):
    """Functional agent for calculating comprehensive risk scores"""
    
    def __init__(self):
        super().__init__(
            name="risk_scoring",
            description="Calculates deterministic risk scores based on anomaly, pattern, and validation findings"
        )
        self.required_context_fields = [
            "transaction_data", 
            "anomaly_results", 
            "pattern_results", 
            "validation_results"
        ]
        self.config = {
            "scoring_rules": {
                "exact_duplicate_invoice": 40,
                "near_duplicate_invoice": 30,
                "unusual_transaction_amount": 20,
                "round_number_amount": 15,
                "common_round_number": 15,
                "weekend_posting": 10,
                "rapid_repeat_payment": 15,
                "threshold_avoidance": 25,
                "dormant_vendor_activity": 15,
                "vendor_payment_spike": 15,
                "unusual_department_spending": 12,
                "vendor_temporal_cluster": 10,
                "department_temporal_cluster": 10,
                "quarter_end_spike": 8,
                "vendor_concentration_risk": 20,
                "vendor_exists_failed": 20,
                "required_fields_failed": 15,
                "invoice_date_validity_failed": 10,
                "approver_authority_failed": 25,
                "reference_consistency_failed": 15
            },
            "risk_levels": {
                "low": (0, 39),
                "medium": (40, 69),
                "high": (70, 100)
            },
            "max_score": 100,
            "flag_threshold_medium": settings.FLAG_THRESHOLD_MEDIUM,
            "flag_threshold_high": settings.FLAG_THRESHOLD_HIGH
        }
    
    def process(self, request: AgentRequest) -> AgentResponse:
        """Calculate comprehensive risk score"""
        start_time = datetime.utcnow()
        
        if not self.validate_request(request):
            return self.create_response(
                result={"error": "Missing required context fields"},
                confidence=0.0,
                processing_time_ms=0
            )
        
        try:
            transaction_data = request.transaction_data
            anomaly_results = request.context.get("anomaly_results", {})
            pattern_results = request.context.get("pattern_results", {})
            validation_results = request.context.get("validation_results", {})
            
            # Extract findings
            anomalies = anomaly_results.get("anomalies", [])
            patterns = pattern_results.get("patterns", [])
            validations = validation_results.get("validations", [])
            
            # Calculate scores
            scoring_breakdown = self._calculate_scoring_breakdown(anomalies, patterns, validations)
            total_score = self._calculate_total_score(scoring_breakdown)
            risk_level = self._determine_risk_level(total_score)
            
            # Determine if transaction should be flagged
            should_flag = self._should_flag_transaction(total_score, risk_level, anomalies, validations)
            
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={
                    "status": "success",
                    "overall_risk_score": total_score,
                    "risk_level": risk_level,
                    "scoring_breakdown": scoring_breakdown,
                    "flag_recommendation": should_flag,
                    "flag_reason": self._get_flag_reason(total_score, risk_level, anomalies, validations),
                    "metadata": {
                        "transaction_id": transaction_data.get("invoice_id"),
                        "vendor_id": transaction_data.get("vendor_id"),
                        "anomalies_count": len(anomalies),
                        "patterns_count": len(patterns),
                        "failed_validations": len([v for v in validations if v.get("status") == "failed"])
                    }
                },
                confidence=0.92,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"Risk scoring failed: {str(e)}")
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={"error": str(e), "status": "failed"},
                confidence=0.0,
                processing_time_ms=processing_time_ms
            )
    
    def _calculate_scoring_breakdown(self, anomalies: List[Dict[str, Any]], 
                                   patterns: List[Dict[str, Any]], 
                                   validations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed scoring breakdown"""
        breakdown = {
            "anomaly_scores": [],
            "pattern_scores": [],
            "validation_scores": [],
            "category_totals": {
                "anomalies": 0,
                "patterns": 0,
                "validations": 0
            },
            "detailed_scores": {}
        }
        
        # Score anomalies
        for anomaly in anomalies:
            anomaly_type = anomaly.get("type", "unknown")
            score = anomaly.get("score", 0)
            
            if anomaly_type in self.config["scoring_rules"]:
                # Use configured score or anomaly score
                configured_score = self.config["scoring_rules"][anomaly_type]
                final_score = max(score, configured_score)
            else:
                final_score = score
            
            breakdown["anomaly_scores"].append({
                "type": anomaly_type,
                "score": final_score,
                "severity": anomaly.get("severity", "low"),
                "description": anomaly.get("description", "")
            })
            breakdown["category_totals"]["anomalies"] += final_score
            
            # Add to detailed scores
            breakdown["detailed_scores"][anomaly_type] = {
                "score": final_score,
                "category": "anomaly",
                "severity": anomaly.get("severity", "low")
            }
        
        # Score patterns
        for pattern in patterns:
            pattern_type = pattern.get("type", "unknown")
            score = pattern.get("score", 0)
            
            if pattern_type in self.config["scoring_rules"]:
                configured_score = self.config["scoring_rules"][pattern_type]
                final_score = max(score, configured_score)
            else:
                final_score = score
            
            breakdown["pattern_scores"].append({
                "type": pattern_type,
                "score": final_score,
                "severity": pattern.get("severity", "low"),
                "description": pattern.get("description", "")
            })
            breakdown["category_totals"]["patterns"] += final_score
            
            # Add to detailed scores
            breakdown["detailed_scores"][pattern_type] = {
                "score": final_score,
                "category": "pattern",
                "severity": pattern.get("severity", "low")
            }
        
        # Score validation failures
        for validation in validations:
            if validation.get("status") == "failed":
                rule = validation.get("rule", "unknown")
                score = validation.get("score", 0)
                
                # Create failure type key
                failure_type = f"{rule}_failed"
                
                if failure_type in self.config["scoring_rules"]:
                    configured_score = self.config["scoring_rules"][failure_type]
                    final_score = max(score, configured_score)
                else:
                    final_score = score
                
                breakdown["validation_scores"].append({
                    "type": failure_type,
                    "score": final_score,
                    "severity": validation.get("severity", "medium"),
                    "description": validation.get("description", ""),
                    "rule": rule
                })
                breakdown["category_totals"]["validations"] += final_score
                
                # Add to detailed scores
                breakdown["detailed_scores"][failure_type] = {
                    "score": final_score,
                    "category": "validation",
                    "severity": validation.get("severity", "medium"),
                    "rule": rule
                }
        
        return breakdown
    
    def _calculate_total_score(self, breakdown: Dict[str, Any]) -> int:
        """Calculate total risk score with capping"""
        category_totals = breakdown.get("category_totals", {})
        total = sum(category_totals.values())
        
        # Cap at maximum score
        return min(total, self.config["max_score"])
    
    def _determine_risk_level(self, score: int) -> str:
        """Determine risk level based on score"""
        for level, (min_score, max_score) in self.config["risk_levels"].items():
            if min_score <= score <= max_score:
                return level
        
        # Default to high if above max
        return "high"
    
    def _should_flag_transaction(self, score: int, risk_level: str, 
                                anomalies: List[Dict[str, Any]], 
                                validations: List[Dict[str, Any]]) -> bool:
        """Determine if transaction should be flagged for review"""
        
        # Always flag high risk
        if risk_level == "high":
            return True
        
        # Flag medium risk if above threshold
        if risk_level == "medium" and score >= self.config["flag_threshold_medium"]:
            return True
        
        # Flag if any high severity anomalies
        high_severity_anomalies = [a for a in anomalies if a.get("severity") == "high"]
        if high_severity_anomalies:
            return True
        
        # Flag if any high severity validation failures
        high_severity_failures = [v for v in validations if v.get("status") == "failed" and v.get("severity") == "high"]
        if high_severity_failures:
            return True
        
        # Flag exact duplicate invoices (even if medium risk)
        exact_duplicates = [a for a in anomalies if a.get("type") == "exact_duplicate_invoice"]
        if exact_duplicates:
            return True
        
        return False
    
    def _get_flag_reason(self, score: int, risk_level: str, 
                        anomalies: List[Dict[str, Any]], 
                        validations: List[Dict[str, Any]]) -> str:
        """Get reason for flagging transaction"""
        reasons = []
        
        if risk_level == "high":
            reasons.append(f"High risk score: {score}/100")
        
        if risk_level == "medium" and score >= self.config["flag_threshold_medium"]:
            reasons.append(f"Medium risk above threshold: {score}/100")
        
        # Check for specific high-risk findings
        high_severity_anomalies = [a for a in anomalies if a.get("severity") == "high"]
        if high_severity_anomalies:
            reasons.append(f"{len(high_severity_anomalies)} high severity anomalies")
        
        exact_duplicates = [a for a in anomalies if a.get("type") == "exact_duplicate_invoice"]
        if exact_duplicates:
            reasons.append("Exact duplicate invoice detected")
        
        high_severity_failures = [v for v in validations if v.get("status") == "failed" and v.get("severity") == "high"]
        if high_severity_failures:
            reasons.append(f"{len(high_severity_failures)} critical validation failures")
        
        if not reasons:
            reasons.append("Risk assessment completed")
        
        return "; ".join(reasons)
    
    def get_scoring_summary(self, breakdown: Dict[str, Any], total_score: int, risk_level: str) -> Dict[str, Any]:
        """Get comprehensive scoring summary"""
        category_totals = breakdown.get("category_totals", {})
        
        return {
            "total_score": total_score,
            "risk_level": risk_level,
            "category_breakdown": {
                "anomalies": {
                    "score": category_totals.get("anomalies", 0),
                    "percentage": (category_totals.get("anomalies", 0) / total_score * 100) if total_score > 0 else 0,
                    "count": len(breakdown.get("anomaly_scores", []))
                },
                "patterns": {
                    "score": category_totals.get("patterns", 0),
                    "percentage": (category_totals.get("patterns", 0) / total_score * 100) if total_score > 0 else 0,
                    "count": len(breakdown.get("pattern_scores", []))
                },
                "validations": {
                    "score": category_totals.get("validations", 0),
                    "percentage": (category_totals.get("validations", 0) / total_score * 100) if total_score > 0 else 0,
                    "count": len(breakdown.get("validation_scores", []))
                }
            },
            "top_findings": self._get_top_findings(breakdown)
        }
    
    def _get_top_findings(self, breakdown: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get top 5 highest scoring findings"""
        all_scores = []
        
        # Collect anomaly scores
        for anomaly in breakdown.get("anomaly_scores", []):
            all_scores.append({
                "type": anomaly["type"],
                "score": anomaly["score"],
                "category": "anomaly",
                "severity": anomaly.get("severity", "low"),
                "description": anomaly.get("description", "")
            })
        
        # Collect pattern scores
        for pattern in breakdown.get("pattern_scores", []):
            all_scores.append({
                "type": pattern["type"],
                "score": pattern["score"],
                "category": "pattern",
                "severity": pattern.get("severity", "low"),
                "description": pattern.get("description", "")
            })
        
        # Collect validation scores
        for validation in breakdown.get("validation_scores", []):
            all_scores.append({
                "type": validation["type"],
                "score": validation["score"],
                "category": "validation",
                "severity": validation.get("severity", "medium"),
                "description": validation.get("description", "")
            })
        
        # Sort by score descending and get top 5
        all_scores.sort(key=lambda x: x["score"], reverse=True)
        return all_scores[:5]