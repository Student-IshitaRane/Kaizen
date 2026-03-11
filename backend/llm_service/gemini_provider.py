import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import asdict
from .llm_interface import LLMInterface, LLMRequest, LLMResponse, BaseProvider
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold, HarmBlockThreshold

logger = logging.getLogger(__name__)

class GeminiProvider(BaseProvider):
    """Google Gemini LLM provider implementation"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-pro"):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Gemini API key (can be set via GEMINI_API_KEY env var)
            model: Gemini model to use
        """
        super().__init__(api_key, model)
        self.provider_name = "gemini"
        
        # Set API key from parameter or environment
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Gemini"""
        try:
            # Prepare the prompt
            full_prompt = f"""{request.prompt}
            
            Context: {json.dumps(request.context, indent=2)}
            
            Please provide a response in {request.response_format} format."""
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            return LLMResponse(
                content=response.text,
                provider="gemini",
                model=self.model_name,
                tokens_used=response.usage_metadata.total_tokens if hasattr(response, 'usage_metadata') else 0,
                latency_ms=0,  # Gemini doesn't provide this
                cached=False
            )
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            raise
    
    def generate_structured(self, request: LLMRequest, schema: Dict[str, Any]) -> LLMResponse:
        """Generate structured response using function calling"""
        try:
            # For Gemini, we can use function calling or structured output
            # For now, we'll use a system prompt approach
            system_prompt = f"""You are a helpful AI assistant. Please respond in JSON format matching this schema:
{json.dumps(schema, indent=2)}

Context: {json.dumps(request.context, indent=2)}

Please provide a response in the exact JSON format specified above."""

            full_prompt = f"""{system_prompt}

User: {request.prompt}

Please provide your response as a valid JSON object matching the schema above."""

            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            return LLMResponse(
                content=response.text,
                provider="gemini",
                model=self.model_name,
                tokens_used=response.usage_metadata.total_tokens if hasattr(response, 'usage_metadata') else 0,
                latency_ms=0,
                cached=False
            )
            
        except Exception as e:
            logger.error(f"Gemini structured generation failed: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return bool(self.api_key and self.model)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "provider": "gemini",
            "model": self.model_name,
            "available": self.is_available(),
            "max_tokens": 8192,
            "supports_structured_output": True
        }