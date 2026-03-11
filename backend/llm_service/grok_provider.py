import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import asdict
from .llm_interface import LLMInterface, LLMRequest, LLMResponse, BaseProvider

logger = logging.getLogger(__name__)

class GrokProvider(BaseProvider):
    """xAI Grok LLM provider implementation"""
    
    def __init__(self, api_key: str = None, model: str = "grok-beta"):
        """
        Initialize Grok provider
        
        Args:
            api_key: Grok API key (can be set via GROK_API_KEY env var)
            model: Grok model to use
        """
        super().__init__(api_key, model)
        self.provider_name = "grok"
        
        # Set API key from parameter or environment
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("Grok API key is required. Set GROK_API_KEY environment variable or pass api_key parameter")
        
        self.model_name = model
        self.base_url = "https://api.x.ai/v1"
        
        # Placeholder for actual Grok client initialization
        # In a real implementation, you would import and configure the Grok client here
        # For now, we'll create a placeholder client
        
        logger.info(f"Grok provider initialized with model: {self.model_name}")
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Grok (hardcoded for demo)"""
        try:
            logger.info(f"Grok generating response for agent: {request.agent_name}")
            
            # HARDCODED: Return realistic audit assistant responses based on the prompt
            prompt_lower = request.prompt.lower()
            
            # Detect question type and provide appropriate response
            if any(word in prompt_lower for word in ['duplicate', 'duplicates', 'same invoice']):
                response_text = """Based on the analysis, duplicate invoices are a significant risk indicator. Here's what you should know:

**Detection Methods:**
- Exact match: Same invoice ID and vendor
- Near-duplicate: Similar invoice IDs, amounts within 5%, dates within 7 days

**Investigation Steps:**
1. Verify if both invoices were actually paid
2. Check payment dates and amounts
3. Contact vendor to confirm legitimate transactions
4. Review approval workflow for both invoices

**Red Flags:**
- Same approver for both invoices
- Payments made within short time period
- Round number amounts
- Weekend or after-hours processing

**Recommendation:** Flag for immediate review if risk score > 70. Request supporting documentation from vendor and verify with accounts payable."""
            
            elif any(word in prompt_lower for word in ['threshold', 'approval limit', 'just below']):
                response_text = """Threshold avoidance is a common fraud pattern. Here's the analysis:

**What is Threshold Avoidance:**
Transactions intentionally kept just below approval limits to avoid higher-level scrutiny. Common thresholds: $10,000, $50,000, $100,000.

**Detection Indicators:**
- Amount is 95-99% of approval threshold
- Multiple transactions to same vendor near threshold
- Unusual splitting of large purchases
- Pattern of amounts like $9,999.99

**Investigation Protocol:**
1. Review vendor's transaction history
2. Check if there are related transactions that could be combined
3. Verify business justification for the specific amount
4. Interview approver about the transaction

**Deloitte Framework Guidance:**
Per the Risk Assessment Framework, threshold avoidance scores 25 points (medium-high risk) and requires:
- Enhanced documentation review
- Approval from next level up
- Vendor relationship assessment

**Action:** Request detailed invoice breakdown and verify goods/services were actually received."""
            
            elif any(word in prompt_lower for word in ['weekend', 'saturday', 'sunday', 'after hours']):
                response_text = """Weekend and after-hours transactions warrant additional scrutiny:

**Why It's Suspicious:**
- Most legitimate business transactions occur during business hours
- Weekend processing may indicate:
  * Unauthorized access
  * Attempt to avoid detection
  * System manipulation
  * Emergency processing (legitimate but unusual)

**Risk Assessment:**
- Low risk (10 points) if occasional and justified
- Medium risk (25 points) if pattern emerges
- High risk (40 points) if combined with other red flags

**Investigation Steps:**
1. Verify who processed the transaction
2. Check system logs for access times
3. Confirm business justification (e.g., emergency purchase)
4. Review approver authorization
5. Check if vendor typically operates on weekends

**Best Practice:**
Implement controls requiring additional approval for weekend transactions above certain thresholds.

**Recommendation:** Document business justification and verify with transaction approver."""
            
            elif any(word in prompt_lower for word in ['round number', 'exact amount', '100000', '10000']):
                response_text = """Round number transactions require attention:

**Why Round Numbers Are Suspicious:**
- Real invoices typically have specific amounts (e.g., $12,347.82)
- Round numbers may indicate:
  * Estimates rather than actual invoices
  * Placeholder amounts
  * Fraudulent transactions
  * Budget manipulation

**Risk Levels:**
- $1,000, $5,000: Low risk (15 points)
- $10,000, $50,000: Medium risk (20 points)
- $100,000+: Higher scrutiny required

**Common Legitimate Reasons:**
- Retainer fees
- Monthly service contracts
- Rent/lease payments
- Subscription services

**Investigation Checklist:**
✓ Request detailed invoice from vendor
✓ Verify contract terms if applicable
✓ Check if amount matches PO or contract
✓ Review supporting documentation
✓ Confirm goods/services received

**Deloitte Guidance:**
Round numbers combined with other red flags (new vendor, weekend posting, threshold avoidance) significantly increase fraud risk.

**Action:** Request itemized invoice breakdown and verify against contract or PO."""
            
            elif any(word in prompt_lower for word in ['vendor spike', 'unusual spending', 'payment increase']):
                response_text = """Vendor payment spikes are critical risk indicators:

**Statistical Analysis:**
A payment spike is defined as spending that exceeds 2 standard deviations from the vendor's historical average.

**Risk Factors:**
- Sudden 200%+ increase: High risk
- New large payment to established vendor: Medium-high risk
- Spike combined with other anomalies: Critical risk

**Possible Explanations:**
**Legitimate:**
- Large capital purchase
- Year-end bulk order
- Contract renewal
- Emergency procurement

**Suspicious:**
- No supporting documentation
- Unusual payment terms
- New bank account for vendor
- Rushed approval process

**Investigation Protocol:**
1. Calculate vendor's 6-month average spending
2. Identify deviation percentage
3. Request purchase justification
4. Verify goods/services received
5. Check for related transactions
6. Review vendor relationship history

**Deloitte Framework:**
Vendor spikes score 15-25 points depending on magnitude. Combined with other factors, can elevate to high risk (70+).

**Immediate Actions:**
- Hold payment if not yet processed
- Request additional documentation
- Verify with department head
- Confirm vendor legitimacy"""
            
            elif any(word in prompt_lower for word in ['risk score', 'scoring', 'how is risk calculated']):
                response_text = """Risk Scoring Methodology:

**Scoring Components:**

1. **Anomaly Detection (0-50 points):**
   - Exact duplicate: 40 points
   - Near duplicate: 30 points
   - Unusual amount: 20 points
   - Round number: 15 points
   - Weekend posting: 10 points

2. **Pattern Analysis (0-30 points):**
   - Vendor payment spike: 15 points
   - Temporal clustering: 10 points
   - Department spending anomaly: 12 points
   - Quarter-end spike: 8 points

3. **Rule Validation (0-25 points):**
   - Threshold avoidance: 25 points
   - Missing approvals: 20 points
   - Invalid vendor: 20 points
   - Policy violations: 15 points

**Risk Levels:**
- **Low (0-39):** Monitor, no immediate action
- **Medium (40-69):** Review within 5 business days
- **High (70-100):** Immediate investigation required

**Score Aggregation:**
Scores are additive but capped at 100. Multiple anomalies compound risk.

**Example:**
- Duplicate invoice (40) + Weekend posting (10) + Round number (15) = 65 (Medium Risk)
- Threshold avoidance (25) + Vendor spike (15) + Unusual amount (20) = 60 (Medium Risk)

**Deloitte Framework Alignment:**
Our scoring aligns with Deloitte's Risk Assessment Framework, incorporating both quantitative and qualitative factors."""
            
            elif any(word in prompt_lower for word in ['what should i do', 'next steps', 'how to investigate']):
                response_text = """Investigation Workflow for Flagged Transactions:

**Step 1: Initial Review (Day 1)**
□ Review transaction details and risk score
□ Identify specific red flags
□ Check transaction history
□ Verify vendor legitimacy

**Step 2: Documentation Gathering (Days 1-2)**
□ Request original invoice from vendor
□ Obtain purchase order or contract
□ Collect approval documentation
□ Review supporting emails/communications

**Step 3: Verification (Days 2-3)**
□ Confirm goods/services received
□ Verify amounts and dates
□ Check payment status
□ Interview transaction approver

**Step 4: Analysis (Days 3-4)**
□ Compare to similar transactions
□ Assess business justification
□ Evaluate control compliance
□ Determine if fraud indicators present

**Step 5: Decision & Action (Day 5)**
□ Approve: Clear for payment
□ Escalate: Refer to senior management
□ Reject: Block payment, investigate further
□ Report: File suspicious activity report if needed

**High-Risk Transactions (70+ score):**
- Immediate hold on payment
- Notify management within 24 hours
- Conduct enhanced due diligence
- Consider forensic review

**Documentation Requirements:**
- All findings must be documented
- Maintain audit trail
- Record decision rationale
- Update case management system

**Escalation Criteria:**
- Suspected fraud
- Amount > $50,000
- Pattern of violations
- Management override of controls"""
            
            else:
                # Default response for general questions
                response_text = f"""I'm your AI Audit Assistant, trained on the Deloitte Risk Assessment Framework and compliance methodologies.

**I can help you with:**
- Understanding risk scores and anomaly types
- Investigating flagged transactions
- Interpreting audit findings
- Compliance guidance
- Best practices for fraud detection

**Common Questions:**
- "Explain duplicate invoice detection"
- "What is threshold avoidance?"
- "How should I investigate vendor payment spikes?"
- "What do weekend transactions indicate?"
- "How is the risk score calculated?"

**Your Question:** {request.prompt[:200]}

**Response:** Based on your question, I recommend reviewing the specific transaction details and comparing them against historical patterns. Each flagged case includes evidence and recommended actions.

Would you like me to explain a specific anomaly type or investigation procedure?"""

            return LLMResponse(
                content=response_text,
                provider="grok",
                model=self.model_name,
                tokens_used=len(response_text.split()),
                latency_ms=300,
                cached=False
            )
            
        except Exception as e:
            logger.error(f"Grok generation failed: {str(e)}")
            raise
    
    def generate_structured(self, request: LLMRequest, schema: Dict[str, Any]) -> LLMResponse:
        """Generate structured response using Grok (placeholder implementation)"""
        try:
            # Placeholder for actual Grok structured generation
            logger.info(f"Grok generating structured response for agent: {request.agent_name}")
            
            # Create a placeholder structured response
            placeholder_data = {
                "analysis_id": "placeholder_123",
                "agent_name": request.agent_name,
                "result": {
                    "status": "completed",
                    "confidence": 0.85,
                    "explanation": "This is a placeholder structured response from Grok.",
                    "recommendations": ["Review this transaction manually", "Check vendor history"]
                },
                "schema_compliant": True
            }
            
            return LLMResponse(
                content=json.dumps(placeholder_data, indent=2),
                provider="grok",
                model=self.model_name,
                tokens_used=200,  # Placeholder
                latency_ms=600,   # Placeholder
                cached=False
            )
            
        except Exception as e:
            logger.error(f"Grok structured generation failed: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Check if Grok is available"""
        return bool(self.api_key and self.model)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "provider": "grok",
            "model": self.model_name,
            "available": self.is_available(),
            "max_tokens": 32768,  # Grok typically has large context
            "supports_structured_output": True,
            "note": "Placeholder implementation - requires actual Grok API integration"
        }