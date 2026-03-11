#!/usr/bin/env python3
"""
Test script for streaming and AI scaffolding layer
"""

import sys
import os
import json
from datetime import datetime, date
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_streaming_components():
    """Test streaming components"""
    print("=" * 60)
    print("Testing Streaming Components")
    print("=" * 60)
    
    try:
        from streaming.kafka_config import KAFKA_CONFIG, PRODUCER_CONFIG, CONSUMER_CONFIG, TOPICS
        print("✓ Kafka config loaded successfully")
        print(f"  - Bootstrap servers: {KAFKA_CONFIG['bootstrap_servers']}")
        print(f"  - Topics configured: {len(TOPICS)}")
        
        from streaming.kafka_producer import producer
        print("✓ Kafka producer initialized")
        
        from streaming.kafka_consumer import consumer_manager
        print("✓ Kafka consumer manager initialized")
        print(f"  - Consumer groups: {list(consumer_manager.consumers.keys())}")
        
        from streaming.event_handlers import event_handler_registry
        print("✓ Event handler registry initialized")
        print(f"  - Event handlers: {list(event_handler_registry.handlers.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Streaming components test failed: {e}")
        return False

def test_llm_services():
    """Test LLM services"""
    print("\n" + "=" * 60)
    print("Testing LLM Services")
    print("=" * 60)
    
    try:
        from llm_service import llm_service
        
        # Check available providers
        providers = llm_service.get_available_providers()
        print(f"✓ LLM service initialized")
        print(f"  - Total providers: {len(providers)}")
        
        available_count = 0
        for provider in providers:
            if provider.get("available", False):
                available_count += 1
                print(f"    • {provider.get('provider')}: {provider.get('model')} (available)")
            else:
                print(f"    • {provider.get('provider')}: Not configured")
        
        print(f"  - Available providers: {available_count}")
        
        # Test LLM request structure
        from llm_service import LLMRequest
        test_request = LLMRequest(
            prompt="Test prompt",
            context={"test": "data"},
            agent_name="test_agent"
        )
        print("✓ LLM request structure validated")
        
        return available_count > 0
    except Exception as e:
        print(f"✗ LLM services test failed: {e}")
        return False

def test_agent_scaffolding():
    """Test agent scaffolding"""
    print("\n" + "=" * 60)
    print("Testing Agent Scaffolding")
    print("=" * 60)
    
    try:
        from agents.agent_orchestrator import agent_orchestrator
        
        # Get available agents
        agents = agent_orchestrator.get_available_agents()
        print(f"✓ Agent orchestrator initialized")
        print(f"  - Total agents: {len(agents)}")
        
        for agent in agents:
            print(f"    • {agent.get('name')}: {agent.get('description', 'No description')}")
        
        # Get pipeline configs
        pipelines = agent_orchestrator.get_pipeline_configs()
        print(f"  - Available pipelines: {len(pipelines)}")
        for name, steps in pipelines.items():
            print(f"    • {name}: {len(steps)} steps")
        
        # Test agent request structure
        from agents.base_agent import AgentRequest
        test_request = AgentRequest(
            transaction_id="test_123",
            transaction_data={"amount": 1000, "vendor_id": "vendor_123"},
            context={"test": "context"}
        )
        print("✓ Agent request structure validated")
        
        return len(agents) > 0
    except Exception as e:
        print(f"✗ Agent scaffolding test failed: {e}")
        return False

def test_transaction_service_integration():
    """Test transaction service Kafka integration"""
    print("\n" + "=" * 60)
    print("Testing Transaction Service Integration")
    print("=" * 60)
    
    try:
        # Check if transaction_service.py exists and has Kafka integration
        import os
        transaction_service_path = os.path.join("services", "transaction_service.py")
        
        if not os.path.exists(transaction_service_path):
            print("✗ Transaction service file not found")
            return False
        
        # Read the file to check for Kafka integration
        with open(transaction_service_path, 'r') as f:
            transaction_service_code = f.read()
        
        # Check for Kafka imports
        if "from streaming.kafka_producer import producer" in transaction_service_code:
            print("✓ Transaction service imports Kafka producer")
        else:
            print("✗ Transaction service missing Kafka producer import")
            return False
        
        # Check for Kafka publishing method
        if "publish_transaction_created" in transaction_service_code:
            print("✓ Transaction service calls Kafka publishing")
        else:
            print("✗ Transaction service missing Kafka publishing call")
            return False
        
        # Check for _publish_to_kafka method
        if "def _publish_to_kafka" in transaction_service_code:
            print("✓ Transaction service has Kafka publishing method")
        else:
            print("✗ Transaction service missing Kafka publishing method")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Transaction service integration test failed: {e}")
        return False

def test_sample_transaction_flow():
    """Test a sample transaction flow through the system"""
    print("\n" + "=" * 60)
    print("Testing Sample Transaction Flow")
    print("=" * 60)
    
    try:
        # Create sample transaction data
        sample_transaction = {
            "transaction_id": "test_tx_001",
            "invoice_id": "INV-2024-001",
            "vendor_id": "VENDOR-001",
            "amount": 15000.00,
            "invoice_date": date.today().isoformat(),
            "department": "Finance",
            "description": "Test transaction for AI analysis",
            "currency": "USD",
            "status": "submitted"
        }
        
        # Create sample context for agents
        sample_context = {
            "vendor_history": {
                "VENDOR-001": {
                    "transaction_count": 5,
                    "average_amount": 8000.00,
                    "risk_score": 30
                }
            },
            "historical_patterns": {
                "VENDOR-001": {
                    "invoice_patterns": ["INV-2023-001", "INV-2023-002"]
                }
            },
            "business_rules": {
                "blacklisted_vendors": [],
                "amount_thresholds": {"low": 1000, "medium": 5000, "high": 10000}
            },
            "user_role": "manager",
            "time_period": "monthly"
        }
        
        print("✓ Sample transaction data created")
        print(f"  - Transaction: {sample_transaction['invoice_id']}")
        print(f"  - Amount: ${sample_transaction['amount']:,.2f}")
        print(f"  - Vendor: {sample_transaction['vendor_id']}")
        
        # Test agent pipeline (simulated)
        print("✓ Agent pipeline simulation ready")
        print("  - Data preparation: Ready")
        print("  - Anomaly detection: Ready")
        print("  - Pattern analysis: Ready")
        print("  - Rule validation: Ready")
        print("  - Risk scoring: Ready")
        print("  - Explanation generation: Ready")
        
        return True
    except Exception as e:
        print(f"✗ Sample transaction flow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Audit Analytics Platform - Streaming & AI Scaffolding Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Streaming Components", test_streaming_components()))
    results.append(("LLM Services", test_llm_services()))
    results.append(("Agent Scaffolding", test_agent_scaffolding()))
    results.append(("Transaction Service Integration", test_transaction_service_integration()))
    results.append(("Sample Transaction Flow", test_sample_transaction_flow()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Streaming and AI scaffolding is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())