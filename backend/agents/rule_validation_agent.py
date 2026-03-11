import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.database.session import get_db
from models.purchase_ledger import PurchaseLedger
from models.vendor import Vendor
from models.user import User
from .base_agent import BaseAgent, AgentRequest, AgentResponse
from core.config import settings

logger = logging.getLogger(__name__)

class RuleValidationAgent(BaseAgent):
    """Functional agent for validating transactions against business rules and compliance"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(
            name="rule_validation",
            description="Validates transactions against business rules, compliance requirements, and internal policies"
        )
        self.required_context_fields = ["transaction_data", "db_session"]
        self.config = {
            "vendor_exists_score": 20,
            "required_fields_score": 15,
            "date_validity_score": 10,
            "approver_authority_score": 25,
            "reference_consistency_score": 15,
            "required_fields": ["invoice_id", "vendor_id", "amount", "invoice_date"],
            "date_validity_days": 365 * 2,  # 2 years max future/past
            "approval_threshold": settings.APPROVAL_THRESHOLD_DEFAULT
        }
        self.db = db_session
    
    def process(self, request: AgentRequest) -> AgentResponse:
        """Validate transaction against business rules"""
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
            
            # Run all validations
            validations = []
            
            # 1. Vendor exists in vendor master
            vendor_validation = self._validate_vendor_exists(transaction_data)
            validations.append(vendor_validation)
            
            # 2. Required fields are present
            required_fields_validation = self._validate_required_fields(transaction_data)
            validations.append(required_fields_validation)
            
            # 3. Invoice date is valid
            date_validation = self._validate_invoice_date(transaction_data)
            validations.append(date_validation)
            
            # 4. Approver authority check
            approver_validation = self._validate_approver_authority(transaction_data)
            validations.append(approver_validation)
            
            # 5. Transaction reference consistency
            reference_validation = self._validate_reference_consistency(transaction_data)
            validations.append(reference_validation)
            
            # 6. Control failure summary
            control_summary = self._create_control_summary(validations)
            
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={
                    "status": "success",
                    "validations": validations,
                    "control_summary": control_summary,
                    "overall_status": self._determine_overall_status(validations),
                    "metadata": {
                        "transaction_id": transaction_data.get("invoice_id"),
                        "vendor_id": transaction_data.get("vendor_id"),
                        "validation_rules_applied": len(validations)
                    }
                },
                confidence=0.95,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"Rule validation failed: {str(e)}")
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={"error": str(e), "status": "failed"},
                confidence=0.0,
                processing_time_ms=processing_time_ms
            )
    
    def _validate_vendor_exists(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Validate vendor exists in vendor master"""
        vendor_id = transaction.get("vendor_id")
        
        validation_result = {
            "rule": "vendor_exists",
            "description": "Vendor must exist in vendor master",
            "status": "passed",
            "severity": "high",
            "score": 0
        }
        
        if not vendor_id:
            validation_result.update({
                "status": "failed",
                "score": self.config["vendor_exists_score"],
                "evidence": {"error": "Vendor ID is missing"},
                "recommendation": "Provide a valid vendor ID"
            })
            return validation_result
        
        try:
            vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
            
            if not vendor:
                validation_result.update({
                    "status": "failed",
                    "score": self.config["vendor_exists_score"],
                    "evidence": {
                        "vendor_id": vendor_id,
                        "error": "Vendor not found in vendor master"
                    },
                    "recommendation": "Register vendor in vendor master or use valid vendor ID"
                })
            else:
                validation_result.update({
                    "evidence": {
                        "vendor_id": vendor_id,
                        "vendor_name": vendor.vendor_name,
                        "vendor_code": vendor.vendor_code,
                        "vendor_status": vendor.status
                    }
                })
        
        except Exception as e:
            validation_result.update({
                "status": "error",
                "score": self.config["vendor_exists_score"],
                "evidence": {"error": f"Validation error: {str(e)}"},
                "recommendation": "Check vendor database connection"
            })
        
        return validation_result
    
    def _validate_required_fields(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all required fields are present and valid"""
        required_fields = self.config["required_fields"]
        missing_fields = []
        invalid_fields = []
        
        for field in required_fields:
            if field not in transaction or transaction[field] is None:
                missing_fields.append(field)
            elif not self._is_field_valid(field, transaction[field]):
                invalid_fields.append(field)
        
        validation_result = {
            "rule": "required_fields",
            "description": "All required fields must be present and valid",
            "status": "passed",
            "severity": "medium",
            "score": 0,
            "evidence": {
                "required_fields": required_fields,
                "missing_fields": [],
                "invalid_fields": []
            }
        }
        
        if missing_fields or invalid_fields:
            validation_result.update({
                "status": "failed",
                "score": self.config["required_fields_score"],
                "evidence": {
                    "required_fields": required_fields,
                    "missing_fields": missing_fields,
                    "invalid_fields": invalid_fields
                },
                "recommendation": f"Provide valid values for: {', '.join(missing_fields + invalid_fields)}"
            })
        
        return validation_result
    
    def _is_field_valid(self, field: str, value: Any) -> bool:
        """Check if field value is valid"""
        if value is None:
            return False
        
        if field == "amount":
            try:
                amount = float(value)
                return amount > 0
            except (ValueError, TypeError):
                return False
        
        elif field == "invoice_date":
            try:
                date_obj = self._parse_date(value)
                return date_obj is not None
            except (ValueError, TypeError):
                return False
        
        elif field in ["invoice_id", "vendor_id"]:
            return bool(str(value).strip())
        
        return True
    
    def _validate_invoice_date(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Validate invoice date is reasonable"""
        invoice_date = transaction.get("invoice_date")
        
        validation_result = {
            "rule": "invoice_date_validity",
            "description": "Invoice date must be valid and within reasonable range",
            "status": "passed",
            "severity": "medium",
            "score": 0,
            "evidence": {}
        }
        
        if not invoice_date:
            validation_result.update({
                "status": "failed",
                "score": self.config["date_validity_score"],
                "evidence": {"error": "Invoice date is missing"},
                "recommendation": "Provide a valid invoice date"
            })
            return validation_result
        
        try:
            date_obj = self._parse_date(invoice_date)
            if not date_obj:
                validation_result.update({
                    "status": "failed",
                    "score": self.config["date_validity_score"],
                    "evidence": {"error": f"Invalid date format: {invoice_date}"},
                    "recommendation": "Use YYYY-MM-DD format"
                })
                return validation_result
            
            today = datetime.utcnow().date()
            max_future = today + timedelta(days=self.config["date_validity_days"])
            max_past = today - timedelta(days=self.config["date_validity_days"])
            
            if date_obj > max_future:
                validation_result.update({
                    "status": "failed",
                    "score": self.config["date_validity_score"],
                    "evidence": {
                        "invoice_date": date_obj.isoformat(),
                        "today": today.isoformat(),
                        "error": f"Date is too far in the future (max: {max_future.isoformat()})"
                    },
                    "recommendation": "Verify invoice date is correct"
                })
            elif date_obj < max_past:
                validation_result.update({
                    "status": "failed",
                    "score": self.config["date_validity_score"],
                    "evidence": {
                        "invoice_date": date_obj.isoformat(),
                        "today": today.isoformat(),
                        "error": f"Date is too far in the past (min: {max_past.isoformat()})"
                    },
                    "recommendation": "Verify invoice date is correct"
                })
            else:
                validation_result["evidence"] = {
                    "invoice_date": date_obj.isoformat(),
                    "is_valid": True,
                    "is_future": date_obj > today,
                    "days_from_today": (date_obj - today).days
                }
        
        except Exception as e:
            validation_result.update({
                "status": "error",
                "score": self.config["date_validity_score"],
                "evidence": {"error": f"Date validation error: {str(e)}"},
                "recommendation": "Check date format and value"
            })
        
        return validation_result
    def _validate_approver_authority(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Validate approver has authority for transaction amount"""
        amount = transaction.get("amount")
        approver_id = transaction.get("approver_id")
        
        validation_result = {
            "rule": "approver_authority",
            "description": "Approver must have authority for transaction amount",
            "status": "passed",
            "severity": "high",
            "score": 0,
            "evidence": {}
        }
        
        if not amount:
            validation_result.update({
                "status": "failed",
                "score": self.config["approver_authority_score"],
                "evidence": {"error": "Transaction amount is missing"},
                "recommendation": "Provide transaction amount"
            })
            return validation_result
        
        try:
            amount_float = float(amount)
            threshold = self.config["approval_threshold"]
            
            # Check if amount exceeds threshold
            if amount_float > threshold:
                if not approver_id:
                    validation_result.update({
                        "status": "failed",
                        "score": self.config["approver_authority_score"],
                        "evidence": {
                            "amount": amount_float,
                            "threshold": threshold,
                            "error": "Approver required for amount above threshold"
                        },
                        "recommendation": f"Assign approver for amounts above ${threshold:,.2f}"
                    })
                else:
                    # TODO: Implement actual approver authority check
                    # For now, just verify approver exists
                    approver = self.db.query(User).filter(User.id == approver_id).first()
                    if not approver:
                        validation_result.update({
                            "status": "failed",
                            "score": self.config["approver_authority_score"],
                            "evidence": {
                                "amount": amount_float,
                                "threshold": threshold,
                                "approver_id": approver_id,
                                "error": "Approver not found"
                            },
                            "recommendation": "Use valid approver ID"
                        })
                    else:
                        validation_result["evidence"] = {
                            "amount": amount_float,
                            "threshold": threshold,
                            "approver_id": approver_id,
                            "approver_name": f"{approver.first_name} {approver.last_name}",
                            "requires_approval": True,
                            "approver_exists": True
                        }
            else:
                validation_result["evidence"] = {
                    "amount": amount_float,
                    "threshold": threshold,
                    "requires_approval": False,
                    "note": "Amount below approval threshold"
                }
        
        except (ValueError, TypeError) as e:
            validation_result.update({
                "status": "error",
                "score": self.config["approver_authority_score"],
                "evidence": {"error": f"Amount validation error: {str(e)}"},
                "recommendation": "Provide valid numeric amount"
            })
        
        return validation_result
    
    def _validate_reference_consistency(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transaction reference consistency"""
        invoice_id = transaction.get("invoice_id")
        po_number = transaction.get("po_number")
        reference_number = transaction.get("reference_number")
        
        validation_result = {
            "rule": "reference_consistency",
            "description": "Transaction references should follow consistent patterns",
            "status": "passed",
            "severity": "low",
            "score": 0,
            "evidence": {}
        }
        
        inconsistencies = []
        
        # Check invoice ID pattern
        if invoice_id:
            if not self._is_valid_invoice_pattern(invoice_id):
                inconsistencies.append(f"Invoice ID '{invoice_id}' doesn't follow standard pattern")
        
        # Check PO number pattern if provided
        if po_number:
            if not self._is_valid_po_pattern(po_number):
                inconsistencies.append(f"PO number '{po_number}' doesn't follow standard pattern")
        
        # Check reference number if provided
        if reference_number:
            if not self._is_valid_reference_pattern(reference_number):
                inconsistencies.append(f"Reference number '{reference_number}' doesn't follow standard pattern")
        
        if inconsistencies:
            validation_result.update({
                "status": "failed",
                "score": self.config["reference_consistency_score"],
                "evidence": {
                    "inconsistencies": inconsistencies,
                    "invoice_id": invoice_id,
                    "po_number": po_number,
                    "reference_number": reference_number
                },
                "recommendation": "Ensure references follow company standards"
            })
        else:
            validation_result["evidence"] = {
                "invoice_id": invoice_id,
                "po_number": po_number,
                "reference_number": reference_number,
                "patterns_valid": True
            }
        
        return validation_result
    
    def _is_valid_invoice_pattern(self, invoice_id: str) -> bool:
        """Check if invoice ID follows standard pattern"""
        import re
        
        patterns = [
            r'^INV-\d{4}-\d{4,6}$',  # INV-YYYY-NNNN
            r'^[A-Z]{2,3}\d{6,8}$',  # AB123456
            r'^\d{8,10}$',  # 12345678
            r'^[A-Z]{2}-\d{4}-\d{4}$'  # XX-YYYY-NNNN
        ]
        
        for pattern in patterns:
            if re.match(pattern, str(invoice_id).strip().upper()):
                return True
        
        return False
    
    def _is_valid_po_pattern(self, po_number: str) -> bool:
        """Check if PO number follows standard pattern"""
        import re
        
        patterns = [
            r'^PO-\d{4}-\d{4,6}$',  # PO-YYYY-NNNN
            r'^[A-Z]{2}PO\d{6,8}$',  # ABPO123456
            r'^\d{8,10}$',  # 12345678
            r'^PUR-\d{4}-\d{4}$'  # PUR-YYYY-NNNN
        ]
        
        for pattern in patterns:
            if re.match(pattern, str(po_number).strip().upper()):
                return True
        
        return False
    
    def _is_valid_reference_pattern(self, reference: str) -> bool:
        """Check if reference follows standard pattern"""
        import re
        
        # Basic validation - not empty and reasonable length
        ref_str = str(reference).strip()
        return bool(ref_str) and 3 <= len(ref_str) <= 50
    
    def _create_control_summary(self, validations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create control failure summary"""
        failed_validations = [v for v in validations if v.get("status") == "failed"]
        error_validations = [v for v in validations if v.get("status") == "error"]
        
        total_score = sum(v.get("score", 0) for v in validations)
        
        return {
            "total_validations": len(validations),
            "passed_validations": len([v for v in validations if v.get("status") == "passed"]),
            "failed_validations": len(failed_validations),
            "error_validations": len(error_validations),
            "total_risk_score": total_score,
            "failed_rules": [v.get("rule") for v in failed_validations],
            "high_severity_failures": len([v for v in failed_validations if v.get("severity") == "high"]),
            "medium_severity_failures": len([v for v in failed_validations if v.get("severity") == "medium"]),
            "low_severity_failures": len([v for v in failed_validations if v.get("severity") == "low"])
        }
    
    def _determine_overall_status(self, validations: List[Dict[str, Any]]) -> str:
        """Determine overall validation status"""
        if any(v.get("status") == "error" for v in validations):
            return "error"
        elif any(v.get("status") == "failed" for v in validations):
            return "failed"
        else:
            return "passed"
    
    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse date from various formats"""
        if isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, str):
            try:
                return datetime.fromisoformat(date_value.replace('Z', '+00:00')).date()
            except ValueError:
                formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"]
                for fmt in formats:
                    try:
                        return datetime.strptime(date_value, fmt).date()
                    except ValueError:
                        continue
        return None