import logging
from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from llm_service.llm_service import llm_service
from llm_service.llm_interface import LLMRequest

logger = logging.getLogger(__name__)

class ExplanationGenerationAgent(BaseAgent):
    """Agent for generating human-readable explanations of analysis results"""
    
    def __init__(self):
        super().__init__(
            name="explanation_generation",
            description="Generates human-readable explanations and summaries of analysis results"
        )
        self.required_context_fields = [
            "transaction_data", 
            "analysis_results", 
            "risk_score",
            "user_context"
        ]
        self.config = {
            "explanation_style": "detailed",  # "brief", "detailed", "executive"
            "include_recommendations": True,
            "include_evidence": True,
            "use_llm": True,
            "llm_provider": "gemini"  # "gemini" or "grok"
        }
    
    def process(self, request: AgentRequest) -> AgentResponse:
        """Generate human-readable explanation of analysis results"""
        start_time = datetime.utcnow()
        
        if not self.validate_request(request):
            return self.create_response(
                result={"error": "Missing required context fields"},
                confidence=0.0,
                processing_time_ms=0
            )
        
        try:
            transaction_data = request.transaction_data
            analysis_results = request.context.get("analysis_results", {})
            risk_score = request.context.get("risk_score", 0)
            user_context = request.context.get("user_context", {})
            
            # Generate explanation
            explanation = self._generate_explanation(
                transaction_data=transaction_data,
                analysis_results=analysis_results,
                risk_score=risk_score,
                user_context=user_context
            )
            
            # Generate summary
            summary = self._generate_summary(explanation, risk_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis_results, risk_score)
            
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={
                    "status": "success",
                    "explanation": explanation,
                    "summary": summary,
                    "recommendations": recommendations,
                    "key_findings": self._extract_key_findings(analysis_results),
                    "explanation_metadata": {
                        "style": self.config["explanation_style"],
                        "generation_method": "llm" if self.config["use_llm"] else "template",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                },
                confidence=0.88,
                processing_time_ms=processing_time_ms,
                metadata={
                    "explanation_length": len(str(explanation)),
                    "key_points_count": len(self._extract_key_findings(analysis_results)),
                    "user_role": user_context.get("role", "auditor")
                }
            )
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return self.create_response(
                result={"error": str(e), "status": "failed"},
                confidence=0.0,
                processing_time_ms=processing_time_ms
            )
    
    def _generate_explanation(self, transaction_data: Dict[str, Any], 
                             analysis_results: Dict[str, Any], 
                             risk_score: float,
                             user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive explanation"""
        
        if self.config["use_llm"] and llm_service.is_any_provider_available():
            return self._generate_explanation_with_llm(
                transaction_data, analysis_results, risk_score, user_context
            )
        else:
            return self._generate_explanation_with_template(
                transaction_data, analysis_results, risk_score, user_context
            )
    
    def _generate_explanation_with_llm(self, transaction_data: Dict[str, Any], 
                                      analysis_results: Dict[str, Any], 
                                      risk_score: float,
                                      user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation using LLM"""
        try:
            # Prepare context for LLM
            llm_context = {
                "transaction_data": transaction_data,
                "analysis_results": analysis_results,
                "risk_score": risk_score,
                "user_context": user_context,
                "explanation_style": self.config["explanation_style"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Prepare prompt
            prompt = self._build_llm_prompt(transaction_data, analysis_results, risk_score, user_context)
            
            # Create LLM request
            llm_request = LLMRequest(
                prompt=prompt,
                context=llm_context,
                agent_name=self.name,
                temperature=0.7,
                max_tokens=1500,
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
                import json
                try:
                    explanation_data = json.loads(llm_response.content)
                    return explanation_data
                except json.JSONDecodeError:
                    # Fallback to template if JSON parsing fails
                    logger.warning("LLM response not valid JSON, falling back to template")
                    return self._generate_explanation_with_template(
                        transaction_data, analysis_results, risk_score, user_context
                    )
            
        except Exception as e:
            logger.error(f"LLM explanation generation failed: {e}")
        
        # Fallback to template method
        return self._generate_explanation_with_template(
            transaction_data, analysis_results, risk_score, user_context
        )
    
    def _generate_explanation_with_template(self, transaction_data: Dict[str, Any], 
                                           analysis_results: Dict[str, Any], 
                                           risk_score: float,
                                           user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation using template-based approach"""
        
        # Extract key information
        transaction_id = transaction_data.get("invoice_id", "Unknown")
        amount = transaction_data.get("amount", 0)
        vendor = transaction_data.get("vendor_id", "Unknown")
        
        # Get analysis components
        anomalies = analysis_results.get("anomalies", [])
        validations = analysis_results.get("validation_results", [])
        patterns = analysis_results.get("patterns", [])
        
        # Build explanation sections
        sections = []
        
        # 1. Transaction Overview
        sections.append({
            "section": "transaction_overview",
            "title": "Transaction Overview",
            "content": f"Transaction {transaction_id} for ${amount:,.2f} with vendor {vendor}."
        })
        
        # 2. Risk Assessment
        risk_level = self._get_risk_level_text(risk_score)
        sections.append({
            "section": "risk_assessment",
            "title": "Risk Assessment",
            "content": f"Overall risk score: {risk_score:.1f}/100 ({risk_level})."
        })
        
        # 3. Key Findings
        key_findings = self._extract_key_findings(analysis_results)
        if key_findings:
            sections.append({
                "section": "key_findings",
                "title": "Key Findings",
                "content": " • " + "\n • ".join(key_findings)
            })
        
        # 4. Anomalies Detected
        if anomalies:
            anomaly_descriptions = [a.get("description", "Unknown anomaly") for a in anomalies[:3]]
            sections.append({
                "section": "anomalies",
                "title": "Anomalies Detected",
                "content": f"Detected {len(anomalies)} anomalies:\n • " + "\n • ".join(anomaly_descriptions)
            })
        
        # 5. Validation Results
        if validations:
            passed = sum(1 for v in validations if v.get("status") == "passed")
            failed = sum(1 for v in validations if v.get("status") == "failed")
            sections.append({
                "section": "validation",
                "title": "Validation Results",
                "content": f"Passed {passed} of {len(validations)} validation rules. {failed} rules failed."
            })
        
        # 6. Patterns Identified
        if patterns:
            pattern_types = set(p.get("type", "unknown") for p in patterns)
            sections.append({
                "section": "patterns",
                "title": "Patterns Identified",
                "content": f"Identified {len(pattern_types)} pattern types: {', '.join(pattern_types)}"
            })
        
        return {
            "sections": sections,
            "overall_summary": self._generate_overall_summary(risk_score, analysis_results),
            "generation_method": "template",
            "style": self.config["explanation_style"]
        }
    
    def _build_llm_prompt(self, transaction_data: Dict[str, Any], 
                         analysis_results: Dict[str, Any], 
                         risk_score: float,
                         user_context: Dict[str, Any]) -> str:
        """Build prompt for LLM explanation generation"""
        
        user_role = user_context.get("role", "auditor")
        explanation_style = self.config["explanation_style"]
        
        prompt = f"""You are an expert audit analyst. Generate a {explanation_style} explanation of the transaction analysis results.

TRANSACTION DATA:
{self._format_transaction_data(transaction_data)}

ANALYSIS RESULTS:
{self._format_analysis_results(analysis_results)}

RISK SCORE: {risk_score:.1f}/100

USER CONTEXT:
- Role: {user_role}
- Experience level: {user_context.get('experience', 'intermediate')}
- Department: {user_context.get('department', 'audit')}

Please generate a comprehensive explanation that includes:
1. Transaction overview
2. Risk assessment summary
3. Key findings from analysis
4. Anomalies detected (if any)
5. Validation results
6. Patterns identified
7. Recommendations for next steps

Format the explanation in a clear, professional manner appropriate for a {user_role}.
Use bullet points for key findings and recommendations.
Keep the explanation {explanation_style} - {'be concise' if explanation_style == 'brief' else 'provide detailed analysis'}.

Return your response as a JSON object with the following structure:
{{
  "sections": [
    {{
      "section": "section_name",
      "title": "Section Title",
      "content": "Section content here..."
    }}
  ],
  "overall_summary": "Brief overall summary here...",
  "key_recommendations": ["Recommendation 1", "Recommendation 2"]
}}"""

        return prompt
    
    def _get_explanation_schema(self) -> Dict[str, Any]:
        """Get JSON schema for LLM response"""
        return {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "section": {"type": "string"},
                            "title": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["section", "title", "content"]
                    }
                },
                "overall_summary": {"type": "string"},
                "key_recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["sections", "overall_summary", "key_recommendations"]
        }
    
    def _generate_summary(self, explanation: Dict[str, Any], risk_score: float) -> str:
        """Generate executive summary"""
        if "overall_summary" in explanation:
            return explanation["overall_summary"]
        
        # Fallback summary
        risk_level = self._get_risk_level_text(risk_score)
        return f"Transaction analysis complete. Risk score: {risk_score:.1f}/100 ({risk_level}). Review recommended findings."
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any], 
                                 risk_score: float) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        if risk_score >= 80:
            recommendations.append("IMMEDIATE REVIEW REQUIRED: High risk transaction")
            recommendations.append("Escalate to senior management and fraud team")
        elif risk_score >= 60:
            recommendations.append("Enhanced review required before approval")
            recommendations.append("Request additional documentation from vendor")
        elif risk_score >= 40:
            recommendations.append("Standard review process recommended")
            recommendations.append("Monitor for similar transactions")
        else:
            recommendations.append("Transaction appears low risk - proceed with standard approval")
        
        # Analysis-based recommendations
        anomalies = analysis_results.get("anomalies", [])
        if len(anomalies) >= 3:
            recommendations.append("Multiple anomalies detected - conduct thorough investigation")
        
        validations = analysis_results.get("validation_results", [])
        failed_validations = [v for v in validations if v.get("status") == "failed"]
        if failed_validations:
            recommendations.append(f"Address {len(failed_validations)} failed validation rules")
        
        return recommendations
    
    def _extract_key_findings(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis results"""
        findings = []
        
        # Extract from anomalies
        anomalies = analysis_results.get("anomalies", [])
        for anomaly in anomalies[:3]:  # Top 3 anomalies
            desc = anomaly.get("description", "")
            if desc:
                findings.append(desc)
        
        # Extract from validations
        validations = analysis_results.get("validation_results", [])
        failed = [v for v in validations if v.get("status") == "failed"]
        for failure in failed[:2]:  # Top 2 failures
            rule = failure.get("rule", "Unknown rule")
            findings.append(f"Failed validation: {rule}")
        
        # Extract from patterns
        patterns = analysis_results.get("patterns", [])
        if patterns:
            pattern_types = set(p.get("type", "unknown") for p in patterns)
            findings.append(f"Patterns detected: {', '.join(pattern_types)}")
        
        return findings
    
    def _get_risk_level_text(self, risk_score: float) -> str:
        """Convert risk score to text level"""
        if risk_score >= 80:
            return "Critical"
        elif risk_score >= 60:
            return "High"
        elif risk_score >= 40:
            return "Medium"
        elif risk_score >= 20:
            return "Low"
        else:
            return "Very Low"