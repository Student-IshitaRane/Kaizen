"""
Quick test script to verify backend endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✓ Health check: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_analysis_step():
    """Test analysis step endpoint with mock data"""
    try:
        response = requests.post(
            f"{BASE_URL}/analysis/run_step",
            json={
                "upload_id": "test_dataset.csv",
                "step_id": "2",
                "step_name": "Anomaly Detection Agent"
            }
        )
        print(f"✓ Analysis step: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Analysis step failed: {e}")
        return False

def test_chatbot():
    """Test chatbot endpoint"""
    try:
        response = requests.post(
            f"{BASE_URL}/chatbot/query",
            json={"query": "What is ERP?"}
        )
        print(f"✓ Chatbot query: {response.status_code}")
        result = response.json()
        print(f"  Response preview: {result.get('text', '')[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Chatbot query failed: {e}")
        return False

def test_flagged_cases():
    """Test flagged cases endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/cases")
        print(f"✓ Flagged cases: {response.status_code}")
        result = response.json()
        print(f"  Cases found: {len(result.get('cases', []))}")
        return True
    except Exception as e:
        print(f"✗ Flagged cases failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Backend API Test Suite")
    print("=" * 60)
    print("\nMake sure the backend is running on http://localhost:8000\n")
    
    tests = [
        ("Health Check", test_health),
        ("Analysis Step", test_analysis_step),
        ("Chatbot Query", test_chatbot),
        ("Flagged Cases", test_flagged_cases),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- Testing: {name} ---")
        results.append(test_func())
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
