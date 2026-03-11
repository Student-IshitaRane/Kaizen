from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json

@dataclass
class LLMRequest:
    """Standardized LLM request"""
    prompt: str
    context: Dict[str, Any]
    agent_name: str
    temperature: float = 0.7
    max_tokens: int = 2000
    response_format: str = "text"  # "text" or "json"

@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    provider: str
    model: str
    tokens_used: int
    latency_ms: int
    cached: bool = False

class LLMInterface(ABC):
    """Abstract interface for LLM providers"""
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text completion"""
        pass
    
    @abstractmethod
    def generate_structured(self, request: LLMRequest, schema: Dict[str, Any]) -> LLMResponse:
        """Generate structured JSON response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get provider and model information"""
        pass


class BaseProvider(LLMInterface, ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.provider_name = self.__class__.__name__
    
    def is_available(self) -> bool:
        """Check if provider is configured and available"""
        return bool(self.api_key and self.model)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            'provider': self.provider_name,
            'model': self.model,
            'available': self.is_available()
        }
    
    def _validate_json_response(self, content: str, schema: Dict[str, Any]) -> bool:
        """Validate JSON response against schema"""
        try:
            response_data = json.loads(content)
            
            # Basic schema validation (placeholder)
            if not isinstance(response_data, dict):
                return False
                
            # Check required fields if specified
            if "required" in schema:
                for field in schema["required"]:
                    if field not in response_data:
                        return False
            
            return True
        except json.JSONDecodeError:
            return False