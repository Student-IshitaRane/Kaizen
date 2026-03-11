from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@dataclass
class AgentRequest:
    """Request for agent processing"""
    transaction_id: str
    transaction_data: Dict[str, Any]
    context: Dict[str, Any]
    agent_config: Dict[str, Any] = None

@dataclass
class AgentResponse:
    """Response from agent processing"""
    agent_name: str
    transaction_id: str
    result: Dict[str, Any]
    confidence: float
    processing_time_ms: int
    timestamp: str
    metadata: Dict[str, Any] = None

class BaseAgent(ABC):
    """Base class for all audit analytics agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.version = "1.0.0"
        self.required_context_fields: List[str] = []
        self.config: Dict[str, Any] = {}
    
    @abstractmethod
    def process(self, request: AgentRequest) -> AgentResponse:
        """Process a transaction and return analysis results"""
        pass
    
    def validate_request(self, request: AgentRequest) -> bool:
        """Validate that request has required context fields"""
        for field in self.required_context_fields:
            if field not in request.context:
                logger.warning(f"Missing required context field '{field}' for agent {self.name}")
                return False
        return True
    
    def prepare_context(self, request: AgentRequest) -> Dict[str, Any]:
        """Prepare context for agent processing"""
        base_context = {
            "agent_name": self.name,
            "transaction_id": request.transaction_id,
            "timestamp": datetime.utcnow().isoformat(),
            "config": self.config
        }
        
        # Merge with request context
        context = {**base_context, **request.context}
        return context
    
    def create_response(self, result: Dict[str, Any], confidence: float, 
                       processing_time_ms: int, metadata: Dict[str, Any] = None) -> AgentResponse:
        """Create standardized agent response"""
        return AgentResponse(
            agent_name=self.name,
            transaction_id="",  # Will be set by caller
            result=result,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "required_context_fields": self.required_context_fields,
            "config": self.config
        }
