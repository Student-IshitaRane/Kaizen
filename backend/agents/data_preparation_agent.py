import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import re
import uuid
from .base_agent import BaseAgent, AgentRequest, AgentResponse

logger = logging.getLogger(__name__)

class DataPreparationAgent(BaseAgent):
    """Functional agent for preparing and cleaning transaction data"""
    
    def __init__(self):
        super().__init__(
            name="data_preparation",
            description="Prepares and cleans transaction data with field normalization, date parsing, and vendor code standardization"
        )
        self.required_context_fields = ["transaction_data"]
        self.config = {
            "clean_missing_values": True,
            "normalize_currencies": True,
            "validate_dates": True,
            "standardize_formats": True,
            "remove_duplicates": True,
            "default_currency": "USD",
            "date_formats": ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"]
        }
    
    def process(self, request: AgentRequest) -> AgentResponse:
        """Process and normalize transaction data"""
        start_time = datetime.utcnow()
        
        if not self.validate_request(request):
            return self.create_response(
                result={"error": "Missing required context fields"},
                confidence=0.0,
                processing_time_ms=0
            )
        
        try:
            transaction_data = request.transaction_data
            
            # Normalize single transaction or batch of rows
            if isinstance(transaction_data, list):
                normalized_rows = []
                seen_rows = set()
                
                for row in transaction_data:
                    normalized = self._normalize_transaction(row)
                    row_hash = self._create_row_hash(normalized)
                    
                    if not self.config["remove_duplicates"] or row_hash not in seen_rows:
                        normalized_rows.append(normalized)
                        seen_rows.add(row_hash)
                
                result_data = normalized_rows
                operation = "batch_normalization"
            else:
                normalized = self._normalize_transaction(transaction_data)
                result_data = normalized
                operation = "single_normalization"
            
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={
                    "status": "success",
                    "operation": operation,
                    "normalized_data": result_data,
                    "metadata": {
                        "original_fields": list(transaction_data.keys()) if isinstance(transaction_data, dict) else "batch",
                        "normalization_steps": self._get_applied_steps()
                    }
                },
                confidence=0.95,
                processing_time_ms=processing_time_ms,
                metadata={
                    "rows_processed": len(result_data) if isinstance(result_data, list) else 1,
                    "duplicates_removed": len(transaction_data) - len(result_data) if isinstance(transaction_data, list) else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Data preparation failed: {str(e)}")
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={"error": str(e), "status": "failed"},
                confidence=0.0,
                processing_time_ms=processing_time_ms
            )
    
    def _normalize_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a single transaction record"""
        normalized = data.copy()
        
        # 1. Field normalization
        normalized = self._normalize_fields(normalized)
        
        # 2. Date parsing and validation
        normalized = self._normalize_dates(normalized)
        
        # 3. Vendor code normalization
        normalized = self._normalize_vendor(normalized)
        
        # 4. Amount cleanup and standardization
        normalized = self._normalize_amounts(normalized)
        
        # 5. Currency normalization
        normalized = self._normalize_currency(normalized)
        
        # 6. Text field standardization
        normalized = self._standardize_text_fields(normalized)
        
        # 7. Add metadata
        normalized["_normalized_at"] = datetime.utcnow().isoformat()
        normalized["_normalization_version"] = "1.0"
        
        return normalized
    
    def _normalize_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize field names and structure"""
        normalized = {}
        field_mappings = {
            "invoice_id": ["invoice_id", "invoice_number", "inv_id", "invoice_no"],
            "vendor_id": ["vendor_id", "vendor_code", "supplier_id", "supplier_code"],
            "amount": ["amount", "total", "value", "invoice_amount"],
            "invoice_date": ["invoice_date", "date", "invoice_dt", "posting_date"],
            "department": ["department", "dept", "cost_center", "business_unit"],
            "description": ["description", "notes", "remarks", "purpose"],
            "currency": ["currency", "curr", "currency_code"],
            "approver_id": ["approver_id", "approver", "approved_by"],
            "status": ["status", "state", "transaction_status"]
        }
        
        for standard_field, possible_names in field_mappings.items():
            for name in possible_names:
                if name in data and data[name] is not None:
                    normalized[standard_field] = data[name]
                    break
            if standard_field not in normalized:
                normalized[standard_field] = None
        
        # Copy any remaining fields
        for key, value in data.items():
            if key not in [name for names in field_mappings.values() for name in names]:
                normalized[key] = value
        
        return normalized
    
    def _normalize_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate dates"""
        normalized = data.copy()
        
        date_fields = ["invoice_date", "posting_date", "approval_date"]
        
        for field in date_fields:
            if field in normalized and normalized[field]:
                try:
                    # Try to parse date
                    date_value = self._parse_date(normalized[field])
                    if date_value:
                        normalized[field] = date_value.isoformat()
                        normalized[f"{field}_is_valid"] = True
                    else:
                        normalized[f"{field}_is_valid"] = False
                except Exception:
                    normalized[f"{field}_is_valid"] = False
        
        return normalized
    
    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse date from various formats"""
        if isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, str):
            date_str = str(date_value).strip()
            
            # Try ISO format first
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            except ValueError:
                pass
            
            # Try other formats
            for fmt in self.config["date_formats"]:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # Try to extract date from string
            date_patterns = [
                r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
                r'(\d{2})/(\d{2})/(\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
                r'(\d{8})'  # YYYYMMDD
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    try:
                        if pattern == r'(\d{4})-(\d{2})-(\d{2})':
                            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                        elif pattern == r'(\d{2})/(\d{2})/(\d{4})':
                            # Try both DD/MM/YYYY and MM/DD/YYYY
                            try:
                                return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
                            except ValueError:
                                return date(int(match.group(3)), int(match.group(1)), int(match.group(2)))
                        elif pattern == r'(\d{8})':
                            date_str = match.group(1)
                            return date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
                    except (ValueError, IndexError):
                        continue
        
        return None
    
    def _normalize_vendor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize vendor codes and names"""
        normalized = data.copy()
        
        if "vendor_id" in normalized and normalized["vendor_id"]:
            vendor_id = str(normalized["vendor_id"]).strip().upper()
            
            # Remove common prefixes/suffixes
            vendor_id = re.sub(r'^(VENDOR|SUPPLIER|VND|SUP)[_\-\s]*', '', vendor_id, flags=re.IGNORECASE)
            vendor_id = re.sub(r'[_\-\s]+$', '', vendor_id)
            
            # Standardize format
            if re.match(r'^[A-Z]{3,4}\d{3,5}$', vendor_id):
                # Already in good format
                pass
            elif re.match(r'^\d+$', vendor_id):
                # Numeric ID, add V prefix
                vendor_id = f"V{vendor_id.zfill(5)}"
            else:
                # Alphanumeric, ensure consistent format
                vendor_id = re.sub(r'[^A-Z0-9]', '', vendor_id)
                if len(vendor_id) < 3:
                    vendor_id = vendor_id.zfill(3)
            
            normalized["vendor_id"] = vendor_id
        
        return normalized
    
    def _normalize_amounts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize amount values"""
        normalized = data.copy()
        
        if "amount" in normalized and normalized["amount"]:
            try:
                amount_str = str(normalized["amount"]).strip()
                
                # Remove currency symbols and thousand separators
                amount_str = re.sub(r'[^\d\.\-]', '', amount_str)
                
                # Convert to Decimal
                amount_decimal = Decimal(amount_str)
                
                # Round to 2 decimal places
                amount_decimal = amount_decimal.quantize(Decimal('0.01'))
                
                normalized["amount"] = float(amount_decimal)
                normalized["amount_decimal"] = str(amount_decimal)
                normalized["amount_is_valid"] = True
                
            except (InvalidOperation, ValueError, TypeError) as e:
                normalized["amount_is_valid"] = False
                normalized["amount_error"] = str(e)
        
        return normalized
    
    def _normalize_currency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize currency codes"""
        normalized = data.copy()
        
        if "currency" in normalized and normalized["currency"]:
            currency = str(normalized["currency"]).strip().upper()
            
            # Standardize common currency codes
            currency_mapping = {
                "USD": ["USD", "US$", "$", "DOLLAR", "US DOLLAR"],
                "EUR": ["EUR", "€", "EURO"],
                "GBP": ["GBP", "£", "POUND"],
                "INR": ["INR", "₹", "RUPEE"],
                "JPY": ["JPY", "¥", "YEN"]
            }
            
            for standard_code, variants in currency_mapping.items():
                if currency in variants:
                    currency = standard_code
                    break
            
            # Ensure 3-letter code
            if len(currency) != 3:
                currency = self.config["default_currency"]
            
            normalized["currency"] = currency
        else:
            normalized["currency"] = self.config["default_currency"]
        
        return normalized
    
    def _standardize_text_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize text field formatting"""
        normalized = data.copy()
        
        text_fields = ["description", "department", "invoice_id"]
        
        for field in text_fields:
            if field in normalized and normalized[field]:
                value = str(normalized[field]).strip()
                
                # Remove extra whitespace
                value = re.sub(r'\s+', ' ', value)
                
                # Capitalize first letter of each word for certain fields
                if field in ["description", "department"]:
                    value = ' '.join(word.capitalize() for word in value.split())
                
                normalized[field] = value
        
        return normalized
    
    def _create_row_hash(self, data: Dict[str, Any]) -> str:
        """Create hash for duplicate detection"""
        key_fields = ["invoice_id", "vendor_id", "amount", "invoice_date"]
        hash_parts = []
        
        for field in key_fields:
            value = data.get(field)
            if value is not None:
                hash_parts.append(str(value))
        
        return "|".join(hash_parts)
    
    def _get_applied_steps(self) -> List[str]:
        """Get list of applied normalization steps"""
        steps = []
        if self.config["clean_missing_values"]:
            steps.append("missing_values_handled")
        if self.config["normalize_currencies"]:
            steps.append("currency_normalized")
        if self.config["validate_dates"]:
            steps.append("dates_validated")
        if self.config["standardize_formats"]:
            steps.append("formats_standardized")
        if self.config["remove_duplicates"]:
            steps.append("duplicates_removed")
        
        return steps