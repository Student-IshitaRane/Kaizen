#!/usr/bin/env python3
"""
Test script to verify anomaly detection works with the test dataset.
This simulates what happens when you upload data and run AI scan.
"""

import sys
import os
import csv
from datetime import datetime, date
from decimal import Decimal
import uuid
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database.session import get_db
from app.database.models.transaction import Transaction
from app.database.models.vendor import Vendor
from app.database.models.user import User
from core.config import settings

# Import agents
from agents.anomaly_detection_agent import AnomalyDetectionAgent
from agents.pattern_analysis_agent import PatternAnalysisAgent
from agents.risk_scoring_agent import RiskScoringAgent
from agents.base_agent import AgentRequest

def setup_database():
    """Setup database connection"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def load_historical_data(db, csv_file_path):
    """Load historical data to establish patterns"""
    print(f"Loading historical data from {csv_file_path}...")
    
    transactions_loaded = 0
    vendors_created = set()
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Skip comment lines
            if row.get('invoice_id', '').startswith('#'):
                continue
            
            # Skip new transactions (we'll process those separately)
            if row['invoice_id'].startswith('INV-2024-'):
                continue
            
            # Create vendor if not exists
            vendor_id = row['vendor_id']
            if vendor_id not in vendors_created:
                vendor = db.query(Vendor).filter(Vendor.vendor_code == vendor_id).first()
                if not vendor:
                    vendor = Vendor(
                        id=uuid.uuid4(),
                        vendor_code=vendor_id,
                        vendor_name=row['vendor_name'],
                        status='active',
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(vendor)
                    vendors_created.add(vendor_id)
            
            # Create transaction
            try:
                transaction = Transaction(
                    id=uuid.uuid4(),
                    invoice_id=row['invoice_id'],
                    vendor_id=uuid.uuid4(),  # Placeholder - would need actual vendor ID
                    amount=Decimal(row['amount']),
                    currency=row.get('currency', 'USD'),
                    invoice_date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                    posting_date=datetime.strptime(row.get('posting_date', row['date']), '%Y-%m-%d').date(),
                    department=row['department'],
                    description=row['description'],
                    status=row.get('status', 'approved'),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(transaction)
                transactions_loaded += 1
                
            except Exception as e:
                print(f"Error loading transaction {row['invoice_id']}: {e}")
    
    try:
        db.commit()
        print(f"Loaded {transactions_loaded} historical transactions")
        print(f"Created {len(vendors_created)} vendors")
    except Exception as e:
        db.rollback()
        print(f"Error committing historical data: {e}")
    
    return transactions_loaded

def test_anomaly_detection(db, transaction_data: Dict[str, Any]):
    """Test anomaly detection for a single transaction"""
    print(f"\nTesting anomaly detection for transaction: {transaction_data['invoice_id']}")
    print(f"Amount: ${transaction_data['amount']}, Vendor: {transaction_data['vendor_id']}")
    
    # Create agents
    anomaly_agent = AnomalyDetectionAgent(db_session=db)
    pattern_agent = PatternAnalysisAgent(db_session=db)
    risk_agent = RiskScoringAgent()
    
    # Create agent request
    request = AgentRequest(
        transaction_data=transaction_data,
        context={"db_session": db}
    )
    
    # Run anomaly detection
    print("\n1. Running Anomaly Detection...")
    anomaly_result = anomaly_agent.process(request)
    
    if anomaly_result.result.get("status") == "success":
        anomalies = anomaly_result.result.get("anomalies", [])
        print(f"   Detected {len(anomalies)} anomalies:")
        for anomaly in anomalies:
            print(f"   - {anomaly['type']}: {anomaly['description']} (Score: {anomaly['score']})")
    else:
        print(f"   Anomaly detection failed: {anomaly_result.result.get('error')}")
    
    # Run pattern analysis
    print("\n2. Running Pattern Analysis...")
    pattern_result = pattern_agent.process(request)
    
    if pattern_result.result.get("status") == "success":
        patterns = pattern_result.result.get("patterns", [])
        print(f"   Detected {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"   - {pattern['type']}: {pattern['description']} (Score: {pattern['score']})")
    else:
        print(f"   Pattern analysis failed: {pattern_result.result.get('error')}")
    
    # Run risk scoring
    print("\n3. Running Risk Scoring...")
    risk_request = AgentRequest(
        transaction_data=transaction_data,
        context={
            "db_session": db,
            "anomaly_results": anomaly_result.result,
            "pattern_results": pattern_result.result,
            "validation_results": {"validations": []}  # Empty validation for test
        }
    )
    
    risk_result = risk_agent.process(risk_request)
    
    if risk_result.result.get("status") == "success":
        risk_score = risk_result.result.get("overall_risk_score", 0)
        risk_level = risk_result.result.get("risk_level", "low")
        should_flag = risk_result.result.get("flag_recommendation", False)
        
        print(f"   Overall Risk Score: {risk_score}/100")
        print(f"   Risk Level: {risk_level}")
        print(f"   Should Flag: {should_flag}")
        
        if should_flag:
            print(f"   Flag Reason: {risk_result.result.get('flag_reason', 'N/A')}")
        
        # Show scoring breakdown
        breakdown = risk_result.result.get("scoring_breakdown", {})
        category_totals = breakdown.get("category_totals", {})
        print(f"   Scoring Breakdown:")
        print(f"     - Anomalies: {category_totals.get('anomalies', 0)} points")
        print(f"     - Patterns: {category_totals.get('patterns', 0)} points")
        print(f"     - Validations: {category_totals.get('validations', 0)} points")
        
        return risk_score, risk_level, should_flag
    else:
        print(f"   Risk scoring failed: {risk_result.result.get('error')}")
        return 0, "low", False

def create_test_transactions():
    """Create test transaction data that should trigger anomalies"""
    test_transactions = [
        {
            "invoice_id": "INV-TEST-DUP",
            "vendor_id": "V-001",
            "vendor_name": "ABC Corp",
            "amount": 15000.00,
            "date": "2024-03-15",
            "department": "Operations",
            "description": "Duplicate invoice test"
        },
        {
            "invoice_id": "INV-TEST-SPIKE",
            "vendor_id": "V-001",
            "vendor_name": "ABC Corp",
            "amount": 85000.00,
            "date": "2024-03-18",
            "department": "Operations",
            "description": "Vendor payment spike test"
        },
        {
            "invoice_id": "INV-TEST-ROUND",
            "vendor_id": "V-004",
            "vendor_name": "New Vendor Inc",
            "amount": 100000.00,
            "date": "2024-03-22",
            "department": "IT",
            "description": "Round number test"
        },
        {
            "invoice_id": "INV-TEST-WEEKEND",
            "vendor_id": "V-002",
            "vendor_name": "XYZ Ltd",
            "amount": 12000.00,
            "date": "2024-03-23",  # Saturday
            "department": "IT",
            "description": "Weekend posting test"
        },
        {
            "invoice_id": "INV-TEST-THRESHOLD",
            "vendor_id": "V-005",
            "vendor_name": "Threshold Vendor",
            "amount": 9999.99,
            "date": "2024-03-25",
            "department": "Finance",
            "description": "Threshold avoidance test"
        }
    ]
    
    return test_transactions

def main():
    """Main test function"""
    print("=" * 60)
    print("ANOMALY DETECTION TEST SCRIPT")
    print("=" * 60)
    
    # Setup database
    db = setup_database()
    
    # Load historical data first
    historical_file = "comprehensive_test_dataset.csv"
    if os.path.exists(historical_file):
        load_historical_data(db, historical_file)
    else:
        print(f"Warning: Historical data file {historical_file} not found")
        print("Agents need historical data to establish patterns for comparison")
    
    # Test with sample transactions
    test_transactions = create_test_transactions()
    
    results = []
    for transaction in test_transactions:
        risk_score, risk_level, should_flag = test_anomaly_detection(db, transaction)
        results.append({
            "invoice_id": transaction["invoice_id"],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "should_flag": should_flag
        })
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    flagged_count = sum(1 for r in results if r["should_flag"])
    high_risk_count = sum(1 for r in results if r["risk_level"] == "high")
    medium_risk_count = sum(1 for r in results if r["risk_level"] == "medium")
    
    print(f"Total transactions tested: {len(results)}")
    print(f"Transactions flagged for review: {flagged_count}")
    print(f"High risk transactions: {high_risk_count}")
    print(f"Medium risk transactions: {medium_risk_count}")
    
    print("\nDetailed Results:")
    for result in results:
        flag_status = "✓ FLAGGED" if result["should_flag"] else "✗ Not flagged"
        print(f"  {result['invoice_id']}: {result['risk_score']}/100 ({result['risk_level']}) - {flag_status}")
    
    # Cleanup
    db.close()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS FOR TESTING:")
    print("=" * 60)
    print("1. First run the seed script to populate database:")
    print("   python scripts/seed_sample_data.py")
    print("\n2. Upload the comprehensive_test_dataset.csv file")
    print("   This contains both historical data and new transactions with anomalies")
    print("\n3. Run 'Commence AI Scan' in the auditor interface")
    print("\n4. Expected results:")
    print("   - Multiple transactions should be flagged")
    print("   - Risk scores should be shown (40+ for medium, 70+ for high risk)")
    print("   - Evidence and investigation recommendations should be generated")
    print("\n5. If still not working, check:")
    print("   - Database connection is working")
    print("   - Agents are properly initialized")
    print("   - CSV file format matches expected schema")

if __name__ == "__main__":
    main()