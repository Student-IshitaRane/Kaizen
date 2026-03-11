import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from agents.data_preparation_agent import DataPreparationAgent
from agents.anomaly_detection_agent import AnomalyDetectionAgent
from agents.pattern_analysis_agent import PatternAnalysisAgent
from agents.rule_validation_agent import RuleValidationAgent
from agents.risk_scoring_agent import RiskScoringAgent
from agents.explanation_generation_agent import ExplanationGenerationAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates the execution of multiple agents in a pipeline"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.pipeline_config = {
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
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        try:
            self.agents["data_preparation"] = DataPreparationAgent()
            logger.info("DataPreparationAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DataPreparationAgent: {e}")
        
        try:
            self.agents["anomaly_detection"] = AnomalyDetectionAgent()
            logger.info("AnomalyDetectionAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AnomalyDetectionAgent: {e}")
        
        try:
            self.agents["pattern_analysis"] = PatternAnalysisAgent()
            logger.info("PatternAnalysisAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PatternAnalysisAgent: {e}")
        
        try:
            self.agents["rule_validation"] = RuleValidationAgent()
            logger.info("RuleValidationAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RuleValidationAgent: {e}")
        
        try:
            self.agents["risk_scoring"] = RiskScoringAgent()
            logger.info("RiskScoringAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RiskScoringAgent: {e}")
        
        try:
            self.agents["explanation_generation"] = ExplanationGenerationAgent()
            logger.info("ExplanationGenerationAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ExplanationGenerationAgent: {e}")
        
        logger.info(f"Total agents initialized: {len(self.agents)}")
    
    def execute_pipeline(self, transaction_data: Dict[str, Any], 
                        context: Dict[str, Any],
                        pipeline_name: str = "default_pipeline") -> Dict[str, Any]:
        """
        Execute a pipeline of agents
        
        Args:
            transaction_data: Raw transaction data
            context: Additional context for agents
            pipeline_name: Name of pipeline to execute
            
        Returns:
            Dictionary with pipeline results
        """
        pipeline_start = datetime.utcnow()
        pipeline_id = str(uuid.uuid4())
        
        logger.info(f"Starting pipeline {pipeline_name} with ID: {pipeline_id}")
        
        # Get pipeline configuration
        pipeline_steps = self.pipeline_config.get(pipeline_name, self.pipeline_config["default_pipeline"])
        
        # Initialize results
        results = {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline_name,
            "start_time": pipeline_start.isoformat(),
            "steps": [],
            "overall_status": "in_progress",
            "transaction_id": transaction_data.get("transaction_id", "unknown")
        }
        
        # Prepare execution context
        execution_context = context.copy()
        execution_context["transaction_data"] = transaction_data
        execution_context["pipeline_id"] = pipeline_id
        
        # Execute each step in the pipeline
        for step_name in pipeline_steps:
            step_result = self._execute_agent_step(
                agent_name=step_name,
                transaction_data=transaction_data,
                context=execution_context,
                previous_results=results
            )
            
            # Update execution context with step results
            if step_result["status"] == "completed":
                execution_context[f"{step_name}_results"] = step_result["agent_response"].result
                execution_context[f"{step_name}_metadata"] = step_result["agent_response"].metadata
                
                # Pass specific results to next agents
                if step_name == "risk_scoring":
                    execution_context["risk_score"] = step_result["agent_response"].result.get("overall_risk_score", 0)
                elif step_name == "anomaly_detection":
                    execution_context["anomaly_results"] = step_result["agent_response"].result
            
            results["steps"].append(step_result)
            
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
        
        # Generate final summary
        results["summary"] = self._generate_pipeline_summary(results)
        
        logger.info(f"Pipeline {pipeline_id} completed with status: {results['overall_status']}")
        
        return results
    
    def _execute_agent_step(self, agent_name: str, 
                           transaction_data: Dict[str, Any],
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
                "critical": True
            }
        
        try:
            # Prepare agent request
            agent_request = AgentRequest(
                transaction_id=transaction_data.get("transaction_id", str(uuid.uuid4())),
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
    
    def execute_single_agent(self, agent_name: str, 
                            transaction_data: Dict[str, Any],
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single agent independently"""
        agent = self.agents.get(agent_name)
        if not agent:
            return {
                "status": "failed",
                "error": f"Agent {agent_name} not found"
            }
        
        try:
            agent_request = AgentRequest(
                transaction_id=transaction_data.get("transaction_id", str(uuid.uuid4())),
                transaction_data=transaction_data,
                context=context,
                agent_config=agent.config
            )
            
            agent_response = agent.process(agent_request)
            
            return {
                "status": "success",
                "agent_name": agent_name,
                "agent_response": agent_response,
                "agent_info": agent.get_info()
            }
            
        except Exception as e:
            logger.error(f"Single agent execution failed for {agent_name}: {str(e)}")
            return {
                "status": "failed",
                "agent_name": agent_name,
                "error": str(e)
            }
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents with their information"""
        agents_info = []
        
        for name, agent in self.agents.items():
            try:
                info = agent.get_info()
                agents_info.append({
                    "name": name,
                    "description": info.get("description", ""),
                    "version": info.get("version", "1.0.0"),
                    "required_context_fields": info.get("required_context_fields", []),
                    "config": info.get("config", {})
                })
            except Exception as e:
                logger.error(f"Failed to get info for agent {name}: {e}")
                agents_info.append({
                    "name": name,
                    "error": str(e),
                    "available": False
                })
        
        return agents_info
    
    def get_pipeline_configs(self) -> Dict[str, List[str]]:
        """Get available pipeline configurations"""
        return self.pipeline_config
    
    def _is_critical_step(self, agent_name: str) -> bool:
        """Determine if an agent step is critical to the pipeline"""
        critical_agents = ["data_preparation", "risk_scoring"]
        return agent_name in critical_agents
    
    def _generate_pipeline_summary(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of pipeline execution"""
        steps = pipeline_results.get("steps", [])
        
        # Calculate metrics
        completed_steps = [s for s in steps if s.get("status") == "completed"]
        failed_steps = [s for s in steps if s.get("status") == "failed"]
        
        total_confidence = sum(s.get("confidence", 0) for s in completed_steps)
        avg_confidence = total_confidence / len(completed_steps) if completed_steps else 0
        
        total_processing_time = sum(s.get("processing_time_ms", 0) for s in steps)
        
        # Get final risk score if available
        final_risk_score = None
        for step in reversed(steps):
            if step.get("agent_name") == "risk_scoring" and step.get("status") == "completed":
                agent_response = step.get("agent_response")
                if agent_response:
                    final_risk_score = agent_response.result.get("overall_risk_score")
                    break
        
        # Get key findings
        key_findings = []
        for step in steps:
            if step.get("status") == "completed":
                agent_response = step.get("agent_response")
                if agent_response and agent_response.result:
                    result = agent_response.result
                    if "key_findings" in result:
                        key_findings.extend(result["key_findings"])
                    elif "anomalies" in result and result["anomalies"]:
                        key_findings.append(f"{len(result['anomalies'])} anomalies detected")
        
        return {
            "total_steps": len(steps),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "average_confidence": round(avg_confidence, 2),
            "total_processing_time_ms": total_processing_time,
            "final_risk_score": final_risk_score,
            "key_findings": key_findings[:5],  # Top 5 findings
            "pipeline_status": pipeline_results.get("overall_status", "unknown")
        }


# Singleton instance
agent_orchestrator = AgentOrchestrator()