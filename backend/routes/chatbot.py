from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
import random
from llm_service import llm_service, LLMRequest

router = APIRouter(prefix="/chatbot", tags=["Rules Assistant Chat"])

class ChatQuery(BaseModel):
    query: str

@router.post("/query")
async def query_rules(req: ChatQuery):
    # Enhanced system prompt for audit assistant
    system_prompt = """You are an expert AI Audit Assistant with deep knowledge of:
- Deloitte Risk Assessment Framework
- Audit compliance methodologies
- Fraud detection patterns
- Financial transaction analysis
- ERP systems and accounting principles
- Internal controls and governance

Provide clear, professional, and actionable responses. When explaining concepts:
1. Define the term clearly
2. Explain its relevance to auditing
3. Provide practical examples
4. Suggest best practices

Be concise but thorough. Use bullet points for clarity when appropriate."""
    
    # Try to use Gemini first (explicitly)
    if llm_service.is_any_provider_available():
        try:
            llm_req = LLMRequest(
                prompt=f"{system_prompt}\n\nUser Question: {req.query}\n\nPlease provide a helpful, professional response:",
                context={
                    "role": "audit_assistant",
                    "framework": "Deloitte Risk Assessment",
                    "user_query": req.query
                },
                agent_name="chatbot",
                response_format="text",
                temperature=0.7  # Slightly higher for more natural responses
            )
            
            # Try Gemini first
            response_obj = llm_service.generate(llm_req, provider_name="gemini")
            
            # If Gemini fails, try Grok
            if not response_obj or not response_obj.content:
                response_obj = llm_service.generate(llm_req, provider_name="grok")
            
            if response_obj and response_obj.content:
                return {
                    "text": response_obj.content,
                    "citations": [
                        f"AI Model: {response_obj.provider.title()} ({response_obj.model})",
                        "Deloitte Risk Assessment Framework",
                        "Audit Compliance Methodologies"
                    ]
                }
        except Exception as e:
            print(f"LLM generation error: {e}")
            # Continue to fallback
            
    # Fallback mock processing if no provider is configured
    await asyncio.sleep(1.5)
    
    # Improved fallback responses
    query_lower = req.query.lower()
    
    if "erp" in query_lower:
        return {
            "text": """**ERP (Enterprise Resource Planning)** is an integrated software system that manages core business processes across an organization.

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
            "citations": ["ERP Systems Overview", "Deloitte IT Audit Guidelines"]
        }
    
    elif "foreign" in query_lower or "offshore" in query_lower:
        return {
            "text": "Based on Deloitte's Risk Assessment Framework (Section 4.2), offshore payments require enhanced due diligence. The risk score of 94 is justified because the payment was routed to an offshore account not associated with the vendor's primary filing. Standard methodology requires a SAR (Suspicious Activity Report) filing for undocumented offshore routing exceeding $10,000.",
            "citations": ["Anti-Money Laundering (AML) Toolkit", "SAR Filing Procedures", "Deloitte Risk Manual 2024"]
        }
    
    elif "duplicate" in query_lower or "split" in query_lower:
        return {
            "text": "Based on Deloitte's Risk Assessment Framework (Section 4.2), transactions that bypass standard approval workflows and match identical amounts within 48 hours strongly indicate 'Split Billing' to avoid procurement limits. I recommend cross-referencing this vendor against the approved Master Vendor List and verifying both transactions were for legitimate business purposes.",
            "citations": ["Deloitte Risk Manual 2024", "Procurement Fraud Guidelines v3"]
        }
    
    elif "weekend" in query_lower or "off-hours" in query_lower:
        return {
            "text": "According to the latest compliance update regarding irregular weekend processing, you should flag this as a 'High Risk Anomaly'. Protocol dictates an immediate freeze on the vendor account pending a manual voucher review by the Senior Audit Manager. Weekend transactions often indicate unauthorized access or attempts to avoid detection.",
            "citations": ["General Controls Policy - Weekend IT Access", "Deloitte Audit Procedures"]
        }
    
    else:
        # Generic helpful response
        return {
            "text": f"""I'm your AI Audit Assistant. I can help you with:

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

**Your Question:** {req.query}

Could you please provide more details or rephrase your question? I'm here to help with any audit-related inquiries.""",
            "citations": ["Deloitte Risk Assessment Framework", "Audit Best Practices"]
        }

    return response
