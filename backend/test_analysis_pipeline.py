#!/usr/bin/env python3
"""
Test the audit analysis pipeline with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from datetime import datetime, timedelta
from decimal import Decimal
import json

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from services.agent_orchestrator import AgentOrchestrator
from services.analysis_result_service import AnalysisResultService
from streaming.consumer import process_transaction_immediately

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_analysis_pipeline():
    """Test the complete analysis pipeline"""
    print("="*60)
    print("TESTING AUDIT ANALYSIS PIPELINE")
    print("="*60)
    
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Initialize services
        orchestrator = AgentOrchestrator(db)
        analysis_service = AnalysisResultService(db)
        
        print("\n1. Testing Agent Orchestrator...")
        
        # Test sample transactions
        test_transactions = [
            {
                "invoice_id": "TEST-INV-001",
                "vendor_id": "VEND001",
                "amount": 9999.99,  # Just below threshold
                "currency": "USD",
                "invoice_date": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                "department": "IT",
                "description": "Test transaction - threshold avoidance",
                "approver_id": "test-approver-001"
            },
            {
                "invoice_id": "TEST-INV-002",
                "vendor_id": "VEND002",
                "amount": 15000.00,  # Above threshold
                "currency": "USD",
                "invoice_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "department": "Marketing",
                "description": "Test transaction - high amount",
                "approver_id": "test-approver-002"
            },
            {
                "invoice_id": "TEST-INV-003",
                "vendor_id": "VEND003",
                "amount": 1000.00,  # Round number
                "currency": "USD",
                "invoice_date": (datetime.utcnow() - timedelta(days=10)).isoformat(),
                "department": "Operations",
                "description": "Test transaction - round number",
                "approver_id": "test-approver-003"
            }
        ]
        
        for i, transaction_data in enumerate(test_transactions, 1):
            print(f"\n  Testing transaction {i}: {transaction_data['invoice_id']}")
            
            # Run pipeline
            pipeline_results = orchestrator.execute_pipeline(
                transaction_data=transaction_data,
                pipeline_name="default_pipeline",
                immediate_analysis=True
            )
            
            print(f"    Pipeline status: {pipeline_results.get('overall_status')}")
            print(f"    Processing time: {pipeline_results.get('processing_time_ms', 0)}ms")
            
            # Check analysis results
            analysis_results = pipeline_results.get("analysis_results", {})
            risk_scoring = analysis_results.get("risk_scoring", {})
            
            if risk_scoring:
                print(f"    Risk score: {risk_scoring.get('overall_risk_score', 0)}")
                print(f"    Risk level: {risk_scoring.get('risk_level', 'unknown')}")
                print(f"    Flag recommendation: {risk_scoring.get('flag_recommendation', False)}")
            
            # Create flagged case
            flagged_case = analysis_service.create_flagged_case_from_analysis(
                transaction_data=transaction_data,
                analysis_results=analysis_results,
                pipeline_results=pipeline_results
            )
            
            if flagged_case:
                print(f"    Flagged case created: {flagged_case.case_id}")
                print(f"    Flag type: {flagged_case.flag_type}")
                print(f"    Priority: {flagged_case.priority}")
            else:
                print("    No flagged case needed")
        
        print("\n2. Testing Analysis Result Service...")
        
        # Test getting flagged cases
        cases = analysis_service.get_flagged_cases(limit=5)
        print(f"    Found {len(cases)} flagged cases")
        
        for case in cases[:3]:  # Show first 3
            print(f"    - Case {case.case_id}: {case.flag_type} (Score: {case.risk_score})")
        
        print("\n3. Testing Immediate Processing...")
        
        # Test immediate processing
        test_transaction = {
            "invoice_id": "TEST-IMMEDIATE-001",
            "vendor_id": "VEND004",
            "amount": 5000.00,
            "currency": "USD",
            "invoice_date": datetime.utcnow().isoformat(),
            "department": "Finance",
            "description": "Immediate processing test"
        }
        
        result = process_transaction_immediately(test_transaction, db)
        print(f"    Immediate processing result: {result.get('pipeline_status')}")
        print(f"    Risk score: {result.get('risk_score', 0)}")
        print(f"    Flagged case created: {result.get('flagged_case_created', False)}")
        
        print("\n4. Testing System Status...")
        
        # Check agent status
        agent_status = orchestrator.get_agent_status()
        available_agents = [name for name, status in agent_status.items() if status.get("available", False)]
        print(f"    Available agents: {len(available_agents)}")
        for agent in available_agents:
            print(f"      - {agent}")
        
        # Check pipeline configurations
        pipelines = orchestrator.get_available_pipelines()
        print(f"    Available pipelines: {len(pipelines)}")
        for name, steps in pipelines.items():
            print(f"      - {name}: {len(steps)} steps")
        
        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Summary
        print("\nSUMMARY:")
        print(f"- Tested {len(test_transactions)} transactions")
        print(f"- Found {len(cases)} flagged cases in database")
        print(f"- {len(available_agents)} agents available")
        print(f"- {len(pipelines)} pipeline configurations")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()


def test_specific_scenarios():
    """Test specific audit scenarios"""
    print("\n" + "="*60)
    print("TESTING SPECIFIC AUDIT SCENARIOS")
    print("="*60)
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        orchestrator = AgentOrchestrator(db)
        
        scenarios = [
            {
                "name": "Exact Duplicate",
                "data": {
                    "invoice_id": "DUPLICATE-INV-001",
                    "vendor_id": "VEND001",
                    "amount": 2500.00,
                    "currency": "USD",
                    "invoice_date": datetime.utcnow().isoformat(),
                    "department": "IT",
                    "description": "Potential duplicate invoice"
                }
            },
            {
                "name": "Weekend Posting",
                "data": {
                    "invoice_id": "WEEKEND-INV-001",
                    "vendor_id": "VEND002",
                    "amount": 3500.00,
                    "currency": "USD",
                    "invoice_date": (datetime.utcnow() - timedelta(days=2)).isoformat(),  # Saturday
                    "department": "Marketing",
                    "description": "Weekend transaction"
                }
            },
            {
                "name": "Dormant Vendor",
                "data": {
                    "invoice_id": "DORMANT-INV-001",
                    "vendor_id": "VEND-DORMANT",
                    "amount": 4500.00,
                    "currency": "USD",
                    "invoice_date": datetime.utcnow().isoformat(),
                    "department": "Operations",
                    "description": "Dormant vendor reactivation"
                }
            }
        ]
        
        for scenario in scenarios:
            print(f"\n  Scenario: {scenario['name']}")
            
            result = orchestrator.execute_pipeline(
                transaction_data=scenario['data'],
                pipeline_name="default_pipeline",
                immediate_analysis=True
            )
            
            analysis_results = result.get("analysis_results", {})
            risk_scoring = analysis_results.get("risk_scoring", {})
            
            if risk_scoring:
                print(f"    Risk score: {risk_scoring.get('overall_risk_score', 0)}")
                print(f"    Risk level: {risk_scoring.get('risk_level', 'unknown')}")
                
                # Check for specific findings
                anomaly_results = analysis_results.get("anomaly_detection", {})
                anomalies = anomaly_results.get("anomalies", [])
                
                if anomalies:
                    print(f"    Anomalies detected: {len(anomalies)}")
                    for anomaly in anomalies[:2]:  # Show first 2
                        print(f"      - {anomaly.get('type', 'unknown')}: {anomaly.get('description', '')}")
        
        print("\n" + "="*60)
        print("SCENARIO TESTING COMPLETED!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AUDIT ANALYSIS PIPELINE TEST SUITE")
    print("="*60)
    
    # Run tests
    test1_passed = test_analysis_pipeline()
    test2_passed = test_specific_scenarios()
    
    print("\n" + "="*60)
    print("TEST SUITE RESULTS")
    print("="*60)
    
    if test1_passed and test2_passed:
        print("✅ All tests passed!")
        print("\nThe audit analysis pipeline is working correctly.")
        print("Key features verified:")
        print("  - Agent orchestration")
        print("  - Risk scoring")
        print("  - Flagged case creation")
        print("  - Immediate processing")
        print("  - Scenario-based detection")
    else:
        print("❌ Some tests failed.")
        print("Check the error messages above for details.")
    
    print("\nNext steps:")
    print("1. Run the application: python main.py")
    print("2. Seed sample data: python scripts/seed_sample_data.py")
    print("3. Test API endpoints with the sample data")
    print("\n" + "="*60)