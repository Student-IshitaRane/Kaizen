from enum import Enum

class UserRole(str, Enum):
    FINANCE = "finance"
    AUDITOR = "auditor"
    ADMIN = "admin"

class DatasetType(str, Enum):
    VENDOR_MASTER = "vendor_master"
    PURCHASE_LEDGER = "purchase_ledger"
    SALES_LEDGER = "sales_ledger"
    GENERAL_LEDGER = "general_ledger"
    BANK_TRANSACTIONS = "bank_transactions"

class CaseStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED_SUSPICIOUS = "confirmed_suspicious"
    FALSE_POSITIVE = "false_positive"
    NEEDS_REVIEW = "needs_review"
    RESOLVED = "resolved"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class FlagType(str, Enum):
    DUPLICATE_INVOICE = "duplicate_invoice"
    ROUND_NUMBER = "round_number"
    WEEKEND_POSTING = "weekend_posting"
    DORMANT_VENDOR = "dormant_vendor"
    THRESHOLD_AVOIDANCE = "threshold_avoidance"
    BENFORD_ANOMALY = "benford_anomaly"
    QUARTER_END_SPIKE = "quarter_end_spike"
    VENDOR_CONCENTRATION = "vendor_concentration"
    APPROVAL_VIOLATION = "approval_violation"
    DATA_VALIDATION = "data_validation"

class TransactionType(str, Enum):
    INVOICE = "invoice"
    PAYMENT = "payment"
    JOURNAL_ENTRY = "journal_entry"
    PURCHASE = "purchase"
    SALE = "sale"

class VendorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"