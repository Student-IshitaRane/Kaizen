"""
Demo Server for Audit Analytics Platform
Works around Python 3.13 + FastAPI/Pydantic compatibility issues
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime

# Mock data for demo
MOCK_FLAGGED_CASES = [
    {
        "id": "case-1",
        "transaction_ref_id": "INV-2024-DUP-001",
        "risk_score": 85,
        "risk_level": "high",
        "flag_type": "duplicate_invoice",
        "reason_summary": "Exact duplicate invoice detected",
        "transaction_amount": 15000.00,
        "transaction_date": "2024-03-15",
        "department": "Operations",
        "vendor_id": "V-001",
        "explanation": "Invoice INV-2024-DUP-001 appears twice with same vendor and amount. This could indicate duplicate payment or fraud.",
        "recommendation": "Verify supporting documentation and contact vendor",
        "status": "new"
    },
    {
        "id": "case-2",
        "transaction_ref_id": "INV-2024-THRESH-001",
        "risk_score": 65,
        "risk_level": "medium",
        "flag_type": "threshold_avoidance",
        "reason_summary": "Threshold avoidance pattern detected",
        "transaction_amount": 9999.99,
        "transaction_date": "2024-03-25",
        "department": "Finance",
        "vendor_id": "V-005",
        "explanation": "Amount $9,999.99 is just below $10,000 approval threshold. This pattern may indicate intentional avoidance of approval process.",
        "recommendation": "Review approval authority limits and investigate vendor relationship",
        "status": "new"
    },
    {
        "id": "case-3",
        "transaction_ref_id": "INV-2024-SPIKE-001",
        "risk_score": 72,
        "risk_level": "high",
        "flag_type": "data_validation",
        "reason_summary": "Vendor payment spike detected",
        "transaction_amount": 85000.00,
        "transaction_date": "2024-03-18",
        "department": "Operations",
        "vendor_id": "V-001",
        "explanation": "Vendor ABC Corp shows $85,000 payment vs historical average of $15,000. This represents a 467% increase from normal spending patterns.",
        "recommendation": "Request additional documentation and verify goods/services received",
        "status": "new"
    },
    {
        "id": "case-4",
        "transaction_ref_id": "INV-2024-WEEKEND-001",
        "risk_score": 45,
        "risk_level": "medium",
        "flag_type": "weekend_posting",
        "reason_summary": "Weekend transaction posting",
        "transaction_amount": 12000.00,
        "transaction_date": "2024-03-23",
        "department": "IT",
        "vendor_id": "V-002",
        "explanation": "Transaction posted on Saturday. Weekend transactions are unusual for this vendor and department.",
        "recommendation": "Verify business justification for weekend processing",
        "status": "new"
    },
    {
        "id": "case-5",
        "transaction_ref_id": "INV-2024-ROUND-001",
        "risk_score": 40,
        "risk_level": "medium",
        "flag_type": "round_number",
        "reason_summary": "Round number transaction amount",
        "transaction_amount": 100000.00,
        "transaction_date": "2024-03-22",
        "department": "IT",
        "vendor_id": "V-004",
        "explanation": "Exact round number amount of $100,000.00. Round numbers can indicate estimates rather than actual invoices.",
        "recommendation": "Request detailed invoice breakdown from vendor",
        "status": "new"
    }
]

AGENT_RESPONSES = {
    "data_preparation": {
        "status": "completed",
        "output": "[SYSTEM]: Normalized raw transaction data for 15 ledger entries in the uploaded dataset. (Processed batch in 750ms)"
    },
    "anomaly_detection": {
        "status": "completed",
        "output": "[SYSTEM]: Scanned 15 transactions. Found 8 anomalies using statistical & rule-based checks on uploaded dataset. (Processed batch in 1250ms)"
    },
    "pattern_analysis": {
        "status": "completed",
        "output": "[SYSTEM]: Scanned 15 transactions. Discovered 5 significant behavioral patterns matching known risk vectors. (Processed batch in 980ms)"
    },
    "rule_validation": {
        "status": "completed",
        "output": "[SYSTEM]: Completed standard controls validation against methodologies. 3 total violations found across 15 transactions. (Processed batch in 1100ms)"
    },
    "risk_scoring": {
        "status": "completed",
        "output": "[SYSTEM]: Risk Scoring Engine finalized scores for 15 transactions. Identified 5 High-Risk cases for manual review. (Processed batch in 850ms)"
    },
    "explanation_generation": {
        "status": "completed",
        "output": "[SYSTEM]: Agent Engine generated narrative summaries for the 5 High-Risk findings. Ready for Auditor review. (Processed batch in 1200ms)"
    }
}

CHATBOT_RESPONSES = {
    "erp": """**ERP (Enterprise Resource Planning)** is an integrated software system that manages core business processes across an organization.

**Key Components:**
- Financial Management (GL, AP, AR)
- Supply Chain Management
- Human Resources
- Manufacturing/Operations
- Customer Relationship Management (CRM)

**Audit Relevance:**
- ERP systems are the primary source of financial data for audits
- Controls within ERP systems are critical for data integrity
- Common ERP systems: SAP, Oracle, Microsoft Dynamics, NetSuite

**Audit Considerations:**
- Access controls and segregation of duties
- Data validation and business rules
- Audit trails and transaction logs
- Integration points between modules

**Best Practice:** Auditors should understand the ERP system's control environment and test key controls within the system.""",
    
    "duplicate": """Based on Deloitte's Risk Assessment Framework (Section 4.2), transactions that bypass standard approval workflows and match identical amounts within 48 hours strongly indicate 'Split Billing' to avoid procurement limits. I recommend cross-referencing this vendor against the approved Master Vendor List and verifying both transactions were for legitimate business purposes.""",
    
    "weekend": """According to the latest compliance update regarding irregular weekend processing, you should flag this as a 'High Risk Anomaly'. Protocol dictates an immediate freeze on the vendor account pending a manual voucher review by the Senior Audit Manager. Weekend transactions often indicate unauthorized access or attempts to avoid detection.""",
    
    "default": """I'm your AI Audit Assistant. I can help you with:

**Audit Analysis:**
- Understanding risk scores and anomaly types
- Investigating flagged transactions
- Interpreting audit findings

**Compliance Guidance:**
- Deloitte Risk Assessment Framework
- Internal controls evaluation
- Fraud detection methodologies

**Common Topics:**
- ERP systems and controls
- Duplicate invoice detection
- Threshold avoidance patterns
- Vendor risk assessment
- Weekend/after-hours transactions

Could you please provide more details or rephrase your question? I'm here to help with any audit-related inquiries."""
}

class DemoHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
    
    def _send_json(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        if self.path == "/" or self.path == "/api":
            self._send_json({
                "message": "Audit Analytics Platform API (Demo Server)",
                "version": "1.0.0",
                "status": "operational",
                "note": "Running compatibility mode for Python 3.13"
            })
        
        elif self.path == "/health":
            self._send_json({
                "status": "healthy",
                "database": "connected",
                "services": "operational"
            })
        
        elif self.path == "/api/cases":
            self._send_json({
                "cases": MOCK_FLAGGED_CASES,
                "total": len(MOCK_FLAGGED_CASES)
            })
        
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        # Analysis step endpoint
        if self.path == "/api/analysis/run_step":
            step_name = data.get("step_name", "")
            
            # Map step name to agent key
            name_map = {
                "Data Ingestion & Normalization": "data_preparation",
                "Anomaly Detection Agent": "anomaly_detection",
                "Pattern Recognition Agent": "pattern_analysis",
                "Compliance Rules Agent": "rule_validation",
                "Risk Scoring Engine": "risk_scoring",
                "LLM Explanation Generation": "explanation_generation"
            }
            
            agent_key = name_map.get(step_name, "data_preparation")
            response = AGENT_RESPONSES.get(agent_key, {"status": "completed", "output": "Step completed"})
            self._send_json(response)
        
        # Chatbot endpoint
        elif self.path == "/api/chatbot/query":
            query = data.get("query", "").lower()
            
            if "erp" in query:
                response_text = CHATBOT_RESPONSES["erp"]
            elif "duplicate" in query or "split" in query:
                response_text = CHATBOT_RESPONSES["duplicate"]
            elif "weekend" in query or "off-hours" in query:
                response_text = CHATBOT_RESPONSES["weekend"]
            else:
                response_text = CHATBOT_RESPONSES["default"]
            
            self._send_json({
                "text": response_text,
                "citations": ["Deloitte Risk Assessment Framework", "Audit Best Practices"]
            })
        
        # Upload endpoint
        elif self.path == "/api/upload":
            self._send_json({
                "message": "Dataset uploaded successfully",
                "upload_id": "demo_upload_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
                "status": "success"
            }, 201)
        
        # Auth endpoints (mock)
        elif self.path == "/api/auth/login":
            self._send_json({
                "access_token": "demo_token_" + datetime.now().strftime("%Y%m%d%H%M%S"),
                "token_type": "bearer",
                "user": {
                    "id": "demo_user",
                    "username": data.get("username", "demo"),
                    "role": "auditor"
                }
            })
        
        elif self.path == "/api/auth/register":
            self._send_json({
                "message": "User registered successfully",
                "user_id": "demo_user_" + datetime.now().strftime("%Y%m%d%H%M%S")
            }, 201)
        
        else:
            self._send_json({"error": "Endpoint not found"}, 404)
    
    def log_message(self, format, *args):
        # Custom logging format
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DemoHandler)
    
    print("=" * 60)
    print("🚀 Audit Analytics Platform - Demo Server")
    print("=" * 60)
    print(f"\n✅ Server running on http://localhost:{port}")
    print(f"✅ API endpoints available at http://localhost:{port}/api")
    print(f"✅ Health check: http://localhost:{port}/health")
    print("\n📝 Note: Running in compatibility mode for Python 3.13")
    print("   This demo server provides all necessary endpoints for the frontend.\n")
    print("Press Ctrl+C to stop the server\n")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
