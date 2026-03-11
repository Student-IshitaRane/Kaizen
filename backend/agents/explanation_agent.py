import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from .base_agent import BaseAgent, AgentRequest, AgentResponse
from llm_service.llm_service import llm_service
from llm_service.llm_interface import LLMRequest
from core.config import settings

logger = logging.getLogger(__name__)

class ExplanationAgent(BaseAgent):
    """Functional agent for generating human-readable explanations using LLM"""
    
    def __init__(self):
        super().__init__(
            name="explanation_generation",
            description="Generates audit-friendly explanations using provider-agnostic LLM service"
        )
        self.required_context_fields = [
            "transaction_data", 
            "anomaly_results", 
            "pattern_results", 
            "validation_results",
            "risk_score_results"
        ]
        self.config = {
            "use_llm": settings.ENABLE_LLM_EXPLANATIONS,
            "llm_provider": settings.LLM_PROVIDER,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "cache_enabled": settings.LLM_CACHE_ENABLED,
            "prompt_directory": "backend/prompts"
        }
    
    def process(self, request: AgentRequest) -> AgentResponse:
        """Generate explanation for audit review"""
        start_time = datetime.utcnow()
        
        if not self.validate_request(request):
            return self.create_response(
                result={"error": "Missing required context fields"},
                confidence=0.0,
                processing_time_ms=0
            )
        
        try:
            transaction_data = request.transaction_data
            anomaly_results = request.context.get("anomaly_results", {})
            pattern_results = request.context.get("pattern_results", {})
            validation_results = request.context.get("validation_results", {})
            risk_score_results = request.context.get("risk_score_results", {})
            
            # Prepare data for explanation
            explanation_data = self._prepare_explanation_data(
                transaction_data, anomaly_results, pattern_results, 
                validation_results, risk_score_results
            )
            
            # Generate explanation
            if self.config["use_llm"] and llm_service.is_any_provider_available():
                explanation = self._generate_llm_explanation(explanation_data)
            else:
                explanation = self._generate_fallback_explanation(explanation_data)
            
            # Generate audit actions
            audit_actions = self._generate_audit_actions(explanation_data)
            
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={
                    "status": "success",
                    "explanation": explanation,
                    "audit_actions": audit_actions,
                    "explanation_data": explanation_data,
                    "generation_method": "llm" if self.config["use_llm"] else "fallback",
                    "metadata": {
                        "transaction_id": transaction_data.get("invoice_id"),
                        "risk_score": risk_score_results.get("overall_risk_score", 0),
                        "risk_level": risk_score_results.get("risk_level", "unknown"),
                        "llm_available": llm_service.is_any_provider_available() if self.config["use_llm"] else False
                    }
                },
                confidence=0.88 if self.config["use_llm"] else 0.75,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={"error": str(e), "status": "failed"},
                confidence=0.0,
                processing_time_ms=processing_time_ms
            )
    
    def _prepare_explanation_data(self, transaction_data: Dict[str, Any], 
                                 anomaly_results: Dict[str, Any], 
                                 pattern_results: Dict[str, Any],
                                 validation_results: Dict[str, Any],
                                 risk_score_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare structured data for explanation generation"""
        
        # Extract key findings
        anomalies = anomaly_results.get("anomalies", [])
        patterns = pattern_results.get("patterns", [])
        validations = validation_results.get("validations", [])
        
        # Create findings summary
        findings_summary = self._create_findings_summary(anomalies, patterns, validations)
        
        # Get scoring breakdown
        scoring_breakdown = risk_score_results.get("scoring_breakdown", {})
        top_findings = self._extract_top_findings(scoring_breakdown)
        
        return {
            "transaction": {
                "invoice_id": transaction_data.get("invoice_id", "Unknown"),
                "vendor_id": transaction_data.get("vendor_id", "Unknown"),
                "vendor_name": self._get_vendor_name(transaction_data.get("vendor_id")),
                "amount": transaction_data.get("amount", 0),
                "currency": transaction_data.get("currency", "USD"),
                "invoice_date": transaction_data.get("invoice_date", "Unknown"),
                "department": transaction_data.get("department", "Unknown"),
                "description": transaction_data.get("description", "No description")
            },
            "risk_assessment": {
                "overall_score": risk_score_results.get("overall_risk_score", 0),
                "risk_level": risk_score_results.get("risk_level", "unknown"),
                "flag_recommendation": risk_score_results.get("flag_recommendation", False),
                "flag_reason": risk_score_results.get("flag_reason", "")
            },
            "findings": {
                "summary": findings_summary,
                "top_findings": top_findings,
                "anomaly_count": len(anomalies),
                "pattern_count": len(patterns),
                "validation_failures": len([v for v in validations if v.get("status") == "failed"]),
                "high_severity_count": len([f for f in anomalies + patterns if f.get("severity") == "high"])
            },
            "scoring_breakdown": {
                "total_score": risk_score_results.get("overall_risk_score", 0),
                "category_totals": scoring_breakdown.get("category_totals", {}),
                "detailed_scores": scoring_breakdown.get("detailed_scores", {})
            }
        }
    
    def _create_findings_summary(self, anomalies: List[Dict[str, Any]], 
                                patterns: List[Dict[str, Any]], 
                                validations: List[Dict[str, Any]]) -> str:
        """Create human-readable findings summary"""
        summary_parts = []
        
        # Add anomaly findings
        if anomalies:
            anomaly_types = set(a.get("type", "unknown") for a in anomalies)
            summary_parts.append(f"Detected {len(anomalies)} anomalies: {', '.join(list(anomaly_types)[:3])}")
        
        # Add pattern findings
        if patterns:
            pattern_types = set(p.get("type", "unknown") for p in patterns)
            summary_parts.append(f"Identified {len(patterns)} patterns: {', '.join(list(pattern_types)[:3])}")
        
        # Add validation findings
        failed_validations = [v for v in validations if v.get("status") == "failed"]
        if failed_validations:
            failed_rules = set(v.get("rule", "unknown") for v in failed_validations)
            summary_parts.append(f"Failed {len(failed_validations)} validations: {', '.join(list(failed_rules))}")
        
        if not summary_parts:
            summary_parts.append("No significant findings detected")
        
        return "; ".join(summary_parts)
    
    def _extract_top_findings(self, scoring_breakdown: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract top findings from scoring breakdown"""
        top_findings = []
        
        # Get top anomaly scores
        for anomaly in scoring_breakdown.get("anomaly_scores", [])[:3]:
            top_findings.append({
                "type": anomaly.get("type", "unknown"),
                "score": anomaly.get("score", 0),
                "category": "anomaly",
                "description": anomaly.get("description", "")
            })
        
        # Get top pattern scores
        for pattern in scoring_breakdown.get("pattern_scores", [])[:2]:
            top_findings.append({
                "type": pattern.get("type", "unknown"),
                "score": pattern.get("score", 0),
                "category": "pattern",
                "description": pattern.get("description", "")
            })
        
        # Get top validation failures
        for validation in scoring_breakdown.get("validation_scores", [])[:2]:
            top_findings.append({
                "type": validation.get("type", "unknown"),
                "score": validation.get("score", 0),
                "category": "validation",
                "description": validation.get("description", "")
            })
        
        # Sort by score and limit to 5
        top_findings.sort(key=lambda x: x["score"], reverse=True)
        return top_findings[:5]
    
    def _get_vendor_name(self, vendor_id: Optional[str]) -> str:
        """Get vendor name from ID (placeholder implementation)"""
        if not vendor_id:
            return "Unknown Vendor"
        
        # TODO: Query vendor database
        # For now, return formatted vendor ID
        return f"Vendor {vendor_id}"
    
    def _generate_llm_explanation(self, explanation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation using LLM"""
        try:
            # Load prompt template
            prompt_template = self._load_prompt_template("explanation_prompt.txt")
            
            # Format prompt with data
            prompt = prompt_template.format(
                invoice_id=explanation_data["transaction"]["invoice_id"],
                vendor_name=explanation_data["transaction"]["vendor_name"],
                vendor_id=explanation_data["transaction"]["vendor_id"],
                amount=explanation_data["transaction"]["amount"],
                currency=explanation_data["transaction"]["currency"],
                invoice_date=explanation_data["transaction"]["invoice_date"],
                department=explanation_data["transaction"]["department"],
                findings_summary=explanation_data["findings"]["summary"],
                risk_score=explanation_data["risk_assessment"]["overall_score"],
                risk_level=explanation_data["risk_assessment"]["risk_level"],
                scoring_breakdown=json.dumps(explanation_data["scoring_breakdown"], indent=2)
            )
            
            # Create LLM request
            llm_request = LLMRequest(
                prompt=prompt,
                context=explanation_data,
                agent_name=self.name,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                response_format="json"
            )
            
            # Get response from LLM
            llm_response = llm_service.generate_structured(
                llm_request,
                schema=self._get_explanation_schema(),
                provider_name=self.config["llm_provider"]
            )
            
            if llm_response:
                # Parse LLM response
                try:
                    explanation = json.loads(llm_response.content)
                    
                    # Validate required fields
                    required_fields = ["reason_summary", "detailed_explanation", "suggested_actions"]
                    if all(field in explanation for field in required_fields):
                        return explanation
                    else:
                        logger.warning("LLM response missing required fields")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse LLM response as JSON: {e}")
            
        except Exception as e:
            logger.warning(f"LLM explanation generation failed: {e}")
        
        # Fallback to template-based explanation
        return self._generate_fallback_explanation(explanation_data)
    
    def _generate_fallback_explanation(self, explanation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback explanation without LLM"""
        transaction = explanation_data["transaction"]
        risk_assessment = explanation_data["risk_assessment"]
        findings = explanation_data["findings"]
        
        # Create reason summary
        if risk_assessment["risk_level"] == "high":
            reason_summary = f"Transaction flagged as HIGH risk ({risk_assessment['overall_score']}/100) due to multiple concerning findings."
        elif risk_assessment["risk_level"] == "medium":
            reason_summary = f"Transaction requires review as MEDIUM risk ({risk_assessment['overall_score']}/100)."
        else:
            reason_summary = f"Transaction assessed as LOW risk ({risk_assessment['overall_score']}/100)."
        
        # Create detailed explanation
        detailed_explanation = [
            f"Transaction {transaction['invoice_id']} for ${transaction['amount']:,.2f} with {transaction['vendor_name']}.",
            f"Risk assessment: {risk_assessment['overall_score']}/100 ({risk_assessment['risk_level'].upper()} risk).",
            f"Findings: {findings['summary']}",
            f"Top concerns: {', '.join([f['type'] for f in findings['top_findings'][:3]])}."
        ]
        
        # Create suggested actions
        if risk_assessment["risk_level"] == "high":
            suggested_actions = [
                "Immediate manual review required",
                "Contact vendor for clarification",
                "Verify supporting documentation",
                "Consider temporary hold on vendor payments"
            ]
        elif risk_assessment["risk_level"] == "medium":
            suggested_actions = [
                "Schedule review within 7 days",
                "Request additional documentation",
                "Verify transaction details with department",
                "Monitor similar transactions"
            ]
        else:
            suggested_actions = [
                "Routine audit sampling",
                "Document review completed",
                "No immediate action required"
            ]
        
        return {
            "reason_summary": reason_summary,
            "detailed_explanation": "\n".join(detailed_explanation),
            "suggested_actions": suggested_actions
        }
    def _generate_audit_actions(self, explanation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific audit actions"""
        risk_level = explanation_data["risk_assessment"]["risk_level"]
        top_findings = explanation_data["findings"]["top_findings"]
        
        # Base actions based on risk level
        if risk_level == "high":
            base_actions = [
                {
                    "action": "Immediate manual review",
                    "rationale": "High risk requires prompt attention to prevent potential issues",
                    "priority": "high",
                    "expected_outcome": "Determine if transaction should be blocked or approved with conditions"
                },
                {
                    "action": "Vendor verification",
                    "rationale": "Ensure vendor legitimacy and transaction authenticity",
                    "priority": "high",
                    "expected_outcome": "Confirm vendor details and transaction purpose"
                }
            ]
        elif risk_level == "medium":
            base_actions = [
                {
                    "action": "Scheduled review within 7 days",
                    "rationale": "Medium risk requires timely but not immediate review",
                    "priority": "medium",
                    "expected_outcome": "Complete review and document findings"
                },
                {
                    "action": "Additional documentation request",
                    "rationale": "Need supporting evidence for risk assessment",
                    "priority": "medium",
                    "expected_outcome": "Obtain complete transaction documentation"
                }
            ]
        else:
            base_actions = [
                {
                    "action": "Routine audit sampling",
                    "rationale": "Low risk transactions included in regular audit sampling",
                    "priority": "low",
                    "expected_outcome": "Confirm transaction compliance with policies"
                }
            ]
        
        # Add specific actions based on findings
        specific_actions = []
        
        for finding in top_findings[:3]:  # Top 3 findings
            if finding["category"] == "anomaly":
                if "duplicate" in finding["type"].lower():
                    specific_actions.append({
                        "action": "Duplicate invoice investigation",
                        "rationale": "Potential duplicate payment or fraud",
                        "priority": "high",
                        "expected_outcome": "Identify and resolve duplicate payment issue"
                    })
                elif "unusual" in finding["type"].lower():
                    specific_actions.append({
                        "action": "Amount verification",
                        "rationale": "Unusual amount requires validation",
                        "priority": "medium",
                        "expected_outcome": "Verify amount matches goods/services received"
                    })
            
            elif finding["category"] == "validation":
                if "vendor_exists" in finding["type"]:
                    specific_actions.append({
                        "action": "Vendor registration check",
                        "rationale": "Vendor not in master requires registration",
                        "priority": "high",
                        "expected_outcome": "Register vendor or use approved vendor"
                    })
                elif "approver_authority" in finding["type"]:
                    specific_actions.append({
                        "action": "Approver authority verification",
                        "rationale": "Ensure approver has proper authority level",
                        "priority": "medium",
                        "expected_outcome": "Confirm approver authorization level"
                    })
        
        # Combine and deduplicate actions
        all_actions = base_actions + specific_actions
        unique_actions = []
        seen_actions = set()
        
        for action in all_actions:
            action_key = action["action"]
            if action_key not in seen_actions:
                unique_actions.append(action)
                seen_actions.add(action_key)
        
        return unique_actions[:5]  # Return top 5 actions
    
    def _load_prompt_template(self, filename: str) -> str:
        """Load prompt template from file"""
        prompt_path = os.path.join(self.config["prompt_directory"], filename)
        
        try:
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Prompt file not found: {prompt_path}")
                # Return default prompt
                if filename == "explanation_prompt.txt":
                    return self._get_default_explanation_prompt()
                else:
                    return self._get_default_audit_action_prompt()
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            return self._get_default_explanation_prompt()
    
    def _get_default_explanation_prompt(self) -> str:
        """Get default explanation prompt"""
        return """You are an expert audit analyst. Generate a concise, structured explanation for a flagged transaction.

TRANSACTION DETAILS:
- Invoice ID: {invoice_id}
- Vendor: {vendor_name} (ID: {vendor_id})
- Amount: {amount} {currency}
- Date: {invoice_date}
- Department: {department}

ANALYSIS FINDINGS:
{findings_summary}

RISK ASSESSMENT:
- Overall Risk Score: {risk_score}/100
- Risk Level: {risk_level}
- Scoring Breakdown: {scoring_breakdown}

Please provide:
1. REASON_SUMMARY (1-2 sentences): Why was this transaction flagged?
2. DETAILED_EXPLANATION (3-5 bullet points): Key audit concerns with evidence.
3. SUGGESTED_ACTIONS (2-3 actionable items): What should the auditor do next?

Format your response as a JSON object with these exact keys:
- "reason_summary"
- "detailed_explanation" 
- "suggested_actions"

Keep the explanation professional, audit-friendly, and focused on the specific findings above."""
    
    def _get_default_audit_action_prompt(self) -> str:
        """Get default audit action prompt"""
        return """You are an audit workflow advisor. Based on the transaction analysis, suggest specific audit actions.

ANALYSIS CONTEXT:
- Transaction Type: Purchase
- Risk Level: {risk_level}
- Key Findings: {key_findings}
- Flag Type: {flag_type}

AUDIT CONSIDERATIONS:
1. Regulatory compliance requirements
2. Internal control effectiveness
3. Fraud detection protocols
4. Vendor management procedures
5. Financial reporting implications

Please provide 3-5 specific, actionable audit steps. Each step should include:
- Action: What to do
- Rationale: Why it's important
- Priority: High/Medium/Low
- Expected Outcome: What to verify

Format as a JSON array of objects with keys: "action", "rationale", "priority", "expected_outcome".

Focus on practical, executable steps for an audit team."""
    
    def _get_explanation_schema(self) -> Dict[str, Any]:
        """Get JSON schema for LLM response"""
        return {
            "type": "object",
            "properties": {
                "reason_summary": {
                    "type": "string",
                    "description": "Brief summary of why transaction was flagged"
                },
                "detailed_explanation": {
                    "type": "string",
                    "description": "Detailed explanation of audit concerns"
                },
                "suggested_actions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of suggested audit actions"
                }
            },
            "required": ["reason_summary", "detailed_explanation", "suggested_actions"]
        }