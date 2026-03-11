import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.database.session import get_db
from core.config import settings

# Import agents
from agents.data_preparation_agent import DataPreparationAgent
from agents.anomaly_detection_agent import AnomalyDetectionAgent
from agents.pattern_analysis_agent import PatternAnalysisAgent
from agents.rule_validation_agent import RuleValidationAgent
from agents.risk_scoring_agent import RiskScoringAgent
from agents.explanation_agent import ExplanationAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates the execution of audit analysis pipeline"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.agents = {}
        self._initialize_agents()
        
        # Pipeline configuration
        self.pipelines = {
            "default_pipeline": [
                "data_preparation",
                "anomaly_detection",
                "pattern_analysis",
                "rule_validation",
                "risk_scoring",
                "explanation_generation"
            ],
            "fast_pipeline": [
                "data_preparation",
                "anomaly_detection",
                "risk_scoring"
            ],
            "compliance_pipeline": [
                "data_preparation",
                "rule_validation",
                "risk_scoring",
                "explanation_generation"
            ]
        }
    
    def _initialize_agents(self):
        """Initialize all agents"""
        try:
            self.agents["data_preparation"] = DataPreparationAgent()
            logger.info("DataPreparationAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DataPreparationAgent: {e}")
        
        try:
            self.agents["anomaly_detection"] = AnomalyDetectionAgent(self.db)
            logger.info("AnomalyDetectionAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AnomalyDetectionAgent: {e}")
        
        try:
            self.agents["pattern_analysis"] = PatternAnalysisAgent(self.db)
            logger.info("PatternAnalysisAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PatternAnalysisAgent: {e}")
        
        try:
            self.agents["rule_validation"] = RuleValidationAgent(self.db)
            logger.info("RuleValidationAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RuleValidationAgent: {e}")
        
        try:
            self.agents["risk_scoring"] = RiskScoringAgent()
            logger.info("RiskScoringAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RiskScoringAgent: {e}")
        
        try:
            self.agents["explanation_generation"] = ExplanationAgent()
            logger.info("ExplanationAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ExplanationAgent: {e}")
    
    def execute_pipeline(self, transaction_data: Dict[str, Any], 
                        pipeline_name: str = "default_pipeline",
                        immediate_analysis: bool = None) -> Dict[str, Any]:
        """
        Execute the full audit analysis pipeline
        
        Args:
            transaction_data: Raw transaction data
            pipeline_name: Name of pipeline to execute
            immediate_analysis: Override ENABLE_IMMEDIATE_ANALYSIS setting
            
        Returns:
            Complete analysis results
        """
        pipeline_start = datetime.utcnow()
        pipeline_id = str(uuid.uuid4())
        
        logger.info(f"Starting pipeline {pipeline_name} with ID: {pipeline_id}")
        
        # Check if immediate analysis is enabled
        if immediate_analysis is None:
            immediate_analysis = settings.ENABLE_IMMEDIATE_ANALYSIS
        
        if not immediate_analysis:
            return {
                "pipeline_id": pipeline_id,
                "status": "skipped",
                "reason": "Immediate analysis disabled",
                "transaction_id": transaction_data.get("invoice_id", "unknown"),
                "timestamp": pipeline_start.isoformat()
            }
        
        # Get pipeline steps
        pipeline_steps = self.pipelines.get(pipeline_name, self.pipelines["default_pipeline"])
        
        # Initialize results
        results = {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline_name,
            "start_time": pipeline_start.isoformat(),
            "transaction_id": transaction_data.get("invoice_id", "unknown"),
            "steps": [],
            "overall_status": "in_progress",
            "analysis_results": {}
        }
        
        # Prepare execution context
        execution_context = {
            "transaction_data": transaction_data,
            "db_session": self.db,
            "pipeline_id": pipeline_id
        }
        
        # Execute each step
        for step_name in pipeline_steps:
            step_result = self._execute_agent_step(
                agent_name=step_name,
                context=execution_context,
                previous_results=results
            )
            
            results["steps"].append(step_result)
            
            # Update execution context with step results
            if step_result["status"] == "completed":
                agent_response = step_result.get("agent_response", {})
                if agent_response and agent_response.result:
                    # Store results for next agents
                    results["analysis_results"][step_name] = agent_response.result
                    
                    # Pass specific results to next agents
                    if step_name == "data_preparation":
                        execution_context["normalized_data"] = agent_response.result.get("normalized_data")
                    elif step_name == "anomaly_detection":
                        execution_context["anomaly_results"] = agent_response.result
                    elif step_name == "pattern_analysis":
                        execution_context["pattern_results"] = agent_response.result
                    elif step_name == "rule_validation":
                        execution_context["validation_results"] = agent_response.result
                    elif step_name == "risk_scoring":
                        execution_context["risk_score_results"] = agent_response.result
                        execution_context["risk_score"] = agent_response.result.get("overall_risk_score", 0)
                        execution_context["risk_level"] = agent_response.result.get("risk_level", "unknown")
            
            # Stop pipeline if critical failure
            if step_result["status"] == "failed" and step_result.get("critical", False):
                results["overall_status"] = "failed"
                logger.error(f"Pipeline {pipeline_id} failed at step {step_name}")
                break
        
        # Determine overall status
        if results["overall_status"] == "in_progress":
            failed_steps = [s for s in results["steps"] if s["status"] == "failed"]
            if failed_steps:
                results["overall_status"] = "partial_success"
            else:
                results["overall_status"] = "success"
        
        # Calculate pipeline metrics
        pipeline_end = datetime.utcnow()
        processing_time_ms = int((pipeline_end - pipeline_start).total_seconds() * 1000)
        
        results["end_time"] = pipeline_end.isoformat()
        results["processing_time_ms"] = processing_time_ms
        results["steps_completed"] = len([s for s in results["steps"] if s["status"] == "completed"])
        results["steps_failed"] = len([s for s in results["steps"] if s["status"] == "failed"])
        
        # Generate final analysis summary
        results["analysis_summary"] = self._generate_analysis_summary(results)
        
        # Determine if transaction should be flagged
        results["flag_recommendation"] = self._determine_flag_recommendation(results)
        
        logger.info(f"Pipeline {pipeline_id} completed with status: {results['overall_status']}")
        
        return results
    
    def _execute_agent_step(self, agent_name: str, 
                           context: Dict[str, Any],
                           previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single agent step"""
        step_start = datetime.utcnow()
        
        logger.info(f"Executing agent step: {agent_name}")
        
        # Get agent instance
        agent = self.agents.get(agent_name)
        if not agent:
            step_end = datetime.utcnow()
            processing_time_ms = int((step_end - step_start).total_seconds() * 1000)
            
            return {
                "agent_name": agent_name,
                "status": "failed",
                "error": f"Agent {agent_name} not found",
                "processing_time_ms": processing_time_ms,
                "start_time": step_start.isoformat(),
                "end_time": step_end.isoformat(),
                "critical": self._is_critical_step(agent_name)
            }
        
        try:
            # Prepare agent request
            from agents.base_agent import AgentRequest
            
            # Get appropriate transaction data
            if agent_name == "data_preparation":
                transaction_data = context["transaction_data"]
            else:
                # Use normalized data if available
                transaction_data = context.get("normalized_data", context["transaction_data"])
            
            agent_request = AgentRequest(
                transaction_id=transaction_data.get("invoice_id", str(uuid.uuid4())),
                transaction_data=transaction_data,
                context=context,
                agent_config=agent.config
            )
            
            # Execute agent
            agent_response = agent.process(agent_request)
            
            step_end = datetime.utcnow()
            processing_time_ms = int((step_end - step_start).total_seconds() * 1000)
            
            return {
                "agent_name": agent_name,
                "status": "completed",
                "agent_response": agent_response,
                "processing_time_ms": processing_time_ms,
                "start_time": step_start.isoformat(),
                "end_time": step_end.isoformat(),
                "confidence": agent_response.confidence,
                "critical": self._is_critical_step(agent_name)
            }
            
        except Exception as e:
            logger.error(f"Agent {agent_name} execution failed: {str(e)}")
            step_end = datetime.utcnow()
            processing_time_ms = int((step_end - step_start).total_seconds() * 1000)
            
            return {
                "agent_name": agent_name,
                "status": "failed",
                "error": str(e),
                "processing_time_ms": processing_time_ms,
                "start_time": step_start.isoformat(),
                "end_time": step_end.isoformat(),
                "critical": self._is_critical_step(agent_name)
            }
    
    def _is_critical_step(self, agent_name: str) -> bool:
        """Determine if an agent step is critical to the pipeline"""
        critical_agents = ["data_preparation", "risk_scoring"]
        return agent_name in critical_agents
    
    def _generate_analysis_summary(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis summary"""
        analysis_results = pipeline_results.get("analysis_results", {})
        
        # Extract key results
        risk_scoring = analysis_results.get("risk_scoring", {})
        explanation = analysis_results.get("explanation_generation", {})
        
        summary = {
            "transaction_id": pipeline_results.get("transaction_id"),
            "pipeline_status": pipeline_results.get("overall_status"),
            "risk_score": risk_scoring.get("overall_risk_score", 0),
            "risk_level": risk_scoring.get("risk_level", "unknown"),
            "flag_recommendation": risk_scoring.get("flag_recommendation", False),
            "processing_time_ms": pipeline_results.get("processing_time_ms", 0)
        }
        
        # Add explanation if available
        if explanation and explanation.get("explanation"):
            summary["reason_summary"] = explanation["explanation"].get("reason_summary", "")
            summary["suggested_actions"] = explanation["explanation"].get("suggested_actions", [])
        
        # Add findings counts
        anomaly_results = analysis_results.get("anomaly_detection", {})
        pattern_results = analysis_results.get("pattern_analysis", {})
        validation_results = analysis_results.get("rule_validation", {})
        
        summary["findings"] = {
            "anomalies": anomaly_results.get("anomalies_detected", 0),
            "patterns": pattern_results.get("patterns_detected", 0),
            "validation_failures": validation_results.get("control_summary", {}).get("failed_validations", 0)
        }
        
        return summary
    
    def _determine_flag_recommendation(self, pipeline_results: Dict[str, Any]) -> bool:
        """Determine if transaction should be flagged based on analysis"""
        analysis_results = pipeline_results.get("analysis_results", {})
        risk_scoring = analysis_results.get("risk_scoring", {})
        
        # Use risk scoring recommendation
        if risk_scoring:
            return risk_scoring.get("flag_recommendation", False)
        
        # Fallback logic
        anomaly_results = analysis_results.get("anomaly_detection", {})
        validation_results = analysis_results.get("rule_validation", {})
        
        # Flag if high severity anomalies
        if anomaly_results.get("summary", {}).get("high_severity_count", 0) > 0:
            return True
        
        # Flag if critical validation failures
        if validation_results.get("control_summary", {}).get("high_severity_failures", 0) > 0:
            return True
        
        return False
    
    def get_available_pipelines(self) -> Dict[str, List[str]]:
        """Get available pipeline configurations"""
        return self.pipelines
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        agent_status = {}
        
        for name, agent in self.agents.items():
            try:
                agent_status[name] = {
                    "available": True,
                    "description": agent.description,
                    "required_fields": agent.required_context_fields
                }
            except Exception as e:
                agent_status[name] = {
                    "available": False,
                    "error": str(e)
                }
        
        return agent_status