#!/usr/bin/env python3
"""
Seed utility for sample audit data
Creates sample vendors, transactions, and flagged cases for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import random
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import get_db
from app.database.models import (
    User, Vendor, Transaction, FlaggedTransaction,
    CaseStatus, RiskLevel
)
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleDataSeeder:
    """Seed sample data for testing and development"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def seed_all(self):
        """Seed all sample data"""
        logger.info("Starting sample data seeding...")
        
        # Seed sample users
        users = self._seed_sample_users()
        logger.info(f"Seeded {len(users)} sample users")
        
        # Seed sample vendors
        vendors = self._seed_sample_vendors()
        logger.info(f"Seeded {len(vendors)} sample vendors")
        
        # Seed sample transactions
        transactions = self._seed_sample_transactions(vendors, users)
        logger.info(f"Seeded {len(transactions)} sample transactions")
        
        # Seed sample flagged cases
        flagged_cases = self._seed_sample_flagged_cases(transactions, vendors, users)
        logger.info(f"Seeded {len(flagged_cases)} sample flagged cases")
        
        logger.info("Sample data seeding completed!")
        
        return {
            "users": len(users),
            "vendors": len(vendors),
            "transactions": len(transactions),
            "flagged_cases": len(flagged_cases)
        }
    
    def _seed_sample_users(self) -> List[User]:
        """Seed sample users"""
        sample_users = [
            {
                "email": "auditor1@example.com",
                "first_name": "Alice",
                "last_name": "Auditor",
                "role": "auditor",
                "department": "Internal Audit"
            },
            {
                "email": "auditor2@example.com",
                "first_name": "Bob",
                "last_name": "Reviewer",
                "role": "auditor",
                "department": "Internal Audit"
            },
            {
                "email": "finance1@example.com",
                "first_name": "Charlie",
                "last_name": "Finance",
                "role": "finance",
                "department": "Accounts Payable"
            },
            {
                "email": "finance2@example.com",
                "first_name": "Diana",
                "last_name": "Approver",
                "role": "finance",
                "department": "Accounts Payable"
            },
            {
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
                "department": "IT"
            }
        ]
        
        users = []
        for user_data in sample_users:
            # Check if user already exists
            existing = self.db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                users.append(existing)
                continue
            
            user = User(
                id=uuid.uuid4(),
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                department=user_data["department"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            # Set a default password (in real app, this would be hashed)
            user.set_password("Password123!")
            
            self.db.add(user)
            users.append(user)
        
        self.db.commit()
        return users
    
    def _seed_sample_vendors(self) -> List[Vendor]:
        """Seed sample vendors"""
        sample_vendors = [
            {
                "vendor_code": "VEND001",
                "vendor_name": "Tech Supplies Inc.",
                "gst_number": "GST00123456",
                "bank_account": "1234567890",
                "contact_person": "John Smith",
                "email": "john@techsupplies.com",
                "phone": "+1-555-123-4567",
                "address": "123 Tech Street",
                "city": "San Francisco",
                "country": "USA",
                "status": "active"
            },
            {
                "vendor_code": "VEND002",
                "vendor_name": "Office Solutions Ltd.",
                "gst_number": "GST00234567",
                "bank_account": "2345678901",
                "contact_person": "Sarah Johnson",
                "email": "sarah@officesolutions.com",
                "phone": "+1-555-234-5678",
                "address": "456 Office Ave",
                "city": "New York",
                "country": "USA",
                "status": "active"
            },
            {
                "vendor_code": "VEND003",
                "vendor_name": "Global Logistics Corp.",
                "gst_number": "GST00345678",
                "bank_account": "3456789012",
                "contact_person": "Mike Wilson",
                "email": "mike@globallogistics.com",
                "phone": "+1-555-345-6789",
                "address": "789 Logistics Blvd",
                "city": "Chicago",
                "country": "USA",
                "status": "active"
            },
            {
                "vendor_code": "VEND004",
                "vendor_name": "Dormant Vendor LLC",
                "gst_number": "GST00456789",
                "bank_account": "4567890123",
                "contact_person": "Tom Brown",
                "email": "tom@dormantvendor.com",
                "phone": "+1-555-456-7890",
                "address": "101 Dormant Lane",
                "city": "Miami",
                "country": "USA",
                "status": "inactive"
            },
            {
                "vendor_code": "VEND005",
                "vendor_name": "High Risk Supplies",
                "gst_number": "GST00567890",
                "bank_account": "5678901234",
                "contact_person": "Lisa Davis",
                "email": "lisa@highrisk.com",
                "phone": "+1-555-567-8901",
                "address": "202 Risk Street",
                "city": "Los Angeles",
                "country": "USA",
                "status": "active"
            }
        ]
        
        vendors = []
        for vendor_data in sample_vendors:
            # Check if vendor already exists
            existing = self.db.query(Vendor).filter(Vendor.vendor_code == vendor_data["vendor_code"]).first()
            if existing:
                vendors.append(existing)
                continue
            
            vendor = Vendor(
                id=uuid.uuid4(),
                vendor_code=vendor_data["vendor_code"],
                vendor_name=vendor_data["vendor_name"],
                gst_number=vendor_data["gst_number"],
                bank_account=vendor_data["bank_account"],
                contact_person=vendor_data["contact_person"],
                email=vendor_data["email"],
                phone=vendor_data["phone"],
                address=vendor_data["address"],
                city=vendor_data["city"],
                country=vendor_data["country"],
                status=vendor_data["status"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(vendor)
            vendors.append(vendor)
        
        self.db.commit()
        return vendors
    
    def _seed_sample_transactions(self, vendors: List[Vendor], users: List[User]) -> List[Transaction]:
        """Seed sample transactions with various risk patterns"""
        
        # Get finance users for approvers
        finance_users = [u for u in users if u.role == "finance"]
        if not finance_users:
            finance_users = users[:2]  # Fallback
        
        transactions = []
        
        # Create normal transactions
        for i in range(20):
            vendor = random.choice(vendors)
            approver = random.choice(finance_users) if finance_users else None
            
            transaction = Transaction(
                id=uuid.uuid4(),
                invoice_id=f"INV-2024-{1000 + i}",
                vendor_id=vendor.id,
                amount=Decimal(str(random.uniform(100, 5000))),
                currency="USD",
                invoice_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                posting_date=datetime.utcnow() - timedelta(days=random.randint(0, 29)),
                department=random.choice(["IT", "Marketing", "Operations", "HR", "Finance"]),
                description=f"Payment for {random.choice(['software', 'office supplies', 'consulting', 'travel', 'equipment'])}",
                approver_id=approver.id if approver else None,
                status="approved",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 29))
            )
            
            self.db.add(transaction)
            transactions.append(transaction)
        
        # Create suspicious transactions for testing
        suspicious_patterns = [
            # Exact duplicate
            {
                "invoice_id": "INV-2024-DUP1",
                "vendor": vendors[0],
                "amount": Decimal("9999.99"),  # Just below threshold
                "description": "Duplicate invoice - suspicious",
                "risk_hint": "exact_duplicate"
            },
            # Near duplicate
            {
                "invoice_id": "INV-2024-DUP2",
                "vendor": vendors[0],
                "amount": Decimal("9995.50"),
                "description": "Similar to previous invoice",
                "risk_hint": "near_duplicate"
            },
            # Weekend posting
            {
                "invoice_id": "INV-2024-WKND",
                "vendor": vendors[1],
                "amount": Decimal("2500.00"),
                "description": "Weekend transaction",
                "risk_hint": "weekend_posting"
            },
            # Round number
            {
                "invoice_id": "INV-2024-ROUND",
                "vendor": vendors[2],
                "amount": Decimal("10000.00"),
                "description": "Exact round number",
                "risk_hint": "round_number"
            },
            # Dormant vendor
            {
                "invoice_id": "INV-2024-DORM",
                "vendor": vendors[3],  # Dormant vendor
                "amount": Decimal("5000.00"),
                "description": "Reactivated dormant vendor",
                "risk_hint": "dormant_vendor"
            }
        ]
        
        for pattern in suspicious_patterns:
            approver = random.choice(finance_users) if finance_users else None
            
            # Create date based on pattern
            if pattern["risk_hint"] == "weekend_posting":
                # Create a Saturday date
                transaction_date = datetime.utcnow() - timedelta(days=7)
                while transaction_date.weekday() != 5:  # Saturday
                    transaction_date -= timedelta(days=1)
            else:
                transaction_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            transaction = Transaction(
                id=uuid.uuid4(),
                invoice_id=pattern["invoice_id"],
                vendor_id=pattern["vendor"].id,
                amount=pattern["amount"],
                currency="USD",
                invoice_date=transaction_date,
                posting_date=transaction_date,
                department=random.choice(["IT", "Marketing", "Operations"]),
                description=pattern["description"],
                approver_id=approver.id if approver else None,
                status="approved",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 29))
            )
            
            self.db.add(transaction)
            transactions.append(transaction)
        
        self.db.commit()
        return transactions
    
    def _seed_sample_flagged_cases(self, transactions: List[Transaction], 
                                  vendors: List[Vendor], 
                                  users: List[User]) -> List[FlaggedTransaction]:
        """Seed sample flagged cases"""
        
        # Get auditor users for assignment
        auditor_users = [u for u in users if u.role == "auditor"]
        
        flagged_cases = []
        
        # Flag some suspicious transactions
        suspicious_transactions = [t for t in transactions if "DUP" in t.invoice_id or "WKND" in t.invoice_id or 
                                  "ROUND" in t.invoice_id or "DORM" in t.invoice_id]
        
        for i, transaction in enumerate(suspicious_transactions[:5]):
            # Determine risk level based on transaction
            if "DUP" in transaction.invoice_id:
                risk_score = random.randint(70, 90)
                risk_level = "high"
                flag_type = "duplicate_payment"
                reason = "Exact or near duplicate invoice detected"
            elif "WKND" in transaction.invoice_id:
                risk_score = random.randint(40, 60)
                risk_level = "medium"
                flag_type = "weekend_posting"
                reason = "Transaction posted on weekend"
            elif "ROUND" in transaction.invoice_id:
                risk_score = random.randint(50, 70)
                risk_level = "medium"
                flag_type = "round_number"
                reason = "Round number transaction amount"
            elif "DORM" in transaction.invoice_id:
                risk_score = random.randint(60, 80)
                risk_level = "high"
                flag_type = "dormant_vendor"
                reason = "Dormant vendor reactivation"
            else:
                risk_score = random.randint(30, 50)
                risk_level = "medium"
                flag_type = "suspicious_pattern"
                reason = "Unusual transaction pattern detected"
            
            # Assign to auditor if available
            assigned_to = random.choice(auditor_users).id if auditor_users else None
            
            flagged_case = FlaggedTransaction(
                id=uuid.uuid4(),
                case_id=f"FLG-{uuid.uuid4().hex[:8].upper()}",
                transaction_id=transaction.id,
                transaction_type="purchase",
                transaction_ref_id=transaction.invoice_id,
                vendor_id=transaction.vendor_id,
                flag_type=flag_type,
                risk_score=risk_score,
                risk_level=risk_level,
                reason_summary=reason,
                detailed_explanation=f"Detailed analysis revealed {reason.lower()}. Requires manual review.",
                suggested_actions=[
                    "Verify supporting documentation",
                    "Contact vendor for clarification",
                    "Review previous transactions with same vendor"
                ],
                status=random.choice(["new", "in_review", "assigned"]),
                priority="high" if risk_level == "high" else "medium",
                assigned_to=assigned_to,
                review_notes="",
                resolution="",
                resolved_by=None,
                resolved_at=None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 6)),
                
                # Store sample analysis metadata
                analysis_metadata={
                    "pipeline_id": str(uuid.uuid4()),
                    "pipeline_name": "default_pipeline",
                    "processing_time_ms": random.randint(500, 2000),
                    "analysis_timestamp": (datetime.utcnow() - timedelta(days=random.randint(1, 7))).isoformat(),
                    "scoring_breakdown": {
                        "anomaly_scores": [
                            {"type": "exact_duplicate_invoice", "score": 40, "severity": "high"},
                            {"type": "weekend_posting", "score": 10, "severity": "low"}
                        ],
                        "pattern_scores": [
                            {"type": "vendor_payment_spike", "score": 15, "severity": "medium"}
                        ],
                        "validation_scores": [],
                        "category_totals": {"anomalies": 50, "patterns": 15, "validations": 0},
                        "detailed_scores": {
                            "exact_duplicate_invoice": {"score": 40, "category": "anomaly", "severity": "high"},
                            "weekend_posting": {"score": 10, "category": "anomaly", "severity": "low"},
                            "vendor_payment_spike": {"score": 15, "category": "pattern", "severity": "medium"}
                        }
                    },
                    "anomaly_summary": {
                        "total_anomalies": 2,
                        "high_severity_count": 1,
                        "medium_severity_count": 0,
                        "low_severity_count": 1,
                        "total_score": 50
                    },
                    "pattern_summary": {
                        "total_patterns": 1,
                        "high_severity_count": 0,
                        "medium_severity_count": 1,
                        "low_severity_count": 0,
                        "total_score": 15
                    },
                    "validation_summary": {
                        "total_validations": 5,
                        "passed_validations": 5,
                        "failed_validations": 0,
                        "error_validations": 0,
                        "total_risk_score": 0
                    }
                }
            )
            
            self.db.add(flagged_case)
            flagged_cases.append(flagged_case)
        
        self.db.commit()
        return flagged_cases
    
    def clear_sample_data(self):
        """Clear all sample data (for testing)"""
        logger.info("Clearing sample data...")
        
        # Delete in reverse order to respect foreign key constraints
        self.db.query(FlaggedTransaction).delete()
        self.db.query(Transaction).delete()
        self.db.query(Vendor).delete()
        
        # Don't delete users as they might be needed for auth
        # self.db.query(User).delete()
        
        self.db.commit()
        logger.info("Sample data cleared!")


def main():
    """Main entry point for seeding sample data"""
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create session
        db = SessionLocal()
        
        # Create seeder and seed data
        seeder = SampleDataSeeder(db)
        
        # Check if user wants to clear existing data
        if len(sys.argv) > 1 and sys.argv[1] == "--clear":
            seeder.clear_sample_data()
            print("Sample data cleared.")
            return
        
        # Seed sample data
        results = seeder.seed_all()
        
        print("\n" + "="*50)
        print("SAMPLE DATA SEEDING COMPLETE")
        print("="*50)
        print(f"Users created: {results['users']}")
        print(f"Vendors created: {results['vendors']}")
        print(f"Transactions created: {results['transactions']}")
        print(f"Flagged cases created: {results['flagged_cases']}")
        print("\nSample credentials:")
        print("- Auditor: auditor1@example.com / Password123!")
        print("- Finance: finance1@example.com / Password123!")
        print("- Admin: admin@example.com / Password123!")
        print("\nUse 'python seed_sample_data.py --clear' to remove sample data")
        
    except Exception as e:
        logger.error(f"Failed to seed sample data: {e}")
        raise
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    main()