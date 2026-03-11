import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import asdict
from .llm_interface import LLMInterface, LLMRequest, LLMResponse
from .gemini_provider import GeminiProvider
from .grok_provider import GrokProvider

logger = logging.getLogger(__name__)

class LLMService:
    """Main LLM service with provider fallback and management"""
    
    def __init__(self):
        self.providers: Dict[str, LLMInterface] = {}
        self.primary_provider = "gemini"
        self.fallback_provider = "grok"
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available LLM providers"""
        try:
            # Initialize Gemini
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.providers["gemini"] = GeminiProvider(api_key=gemini_api_key)
                logger.info("Gemini provider initialized")
            else:
                logger.warning("GEMINI_API_KEY not set, Gemini provider unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {e}")
        
        try:
            # Initialize Grok
            grok_api_key = os.getenv("GROK_API_KEY")
            if grok_api_key:
                self.providers["grok"] = GrokProvider(api_key=grok_api_key)
                logger.info("Grok provider initialized")
            else:
                logger.warning("GROK_API_KEY not set, Grok provider unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize Grok provider: {e}")
        
        if not self.providers:
            logger.warning("No LLM providers available. AI features will be disabled.")
    
    def generate(self, request: LLMRequest, provider_name: Optional[str] = None) -> Optional[LLMResponse]:
        """
        Generate text using specified provider or fallback chain
        
        Args:
            request: LLM request
            provider_name: Specific provider to use (optional)
            
        Returns:
            LLMResponse or None if no providers available
        """
        if provider_name:
            # Use specified provider
            provider = self.providers.get(provider_name)
            if provider and provider.is_available():
                try:
                    return provider.generate(request)
                except Exception as e:
                    logger.error(f"Provider {provider_name} failed: {e}")
                    return self._try_fallback(request, provider_name)
            else:
                logger.warning(f"Provider {provider_name} not available, trying fallback")
                return self._try_fallback(request, provider_name)
        else:
            # Use primary provider with fallback
            return self._generate_with_fallback(request)
    
    def generate_structured(self, request: LLMRequest, schema: Dict[str, Any], 
                          provider_name: Optional[str] = None) -> Optional[LLMResponse]:
        """
        Generate structured response using specified provider or fallback chain
        
        Args:
            request: LLM request
            schema: JSON schema for structured response
            provider_name: Specific provider to use (optional)
            
        Returns:
            LLMResponse or None if no providers available
        """
        if provider_name:
            # Use specified provider
            provider = self.providers.get(provider_name)
            if provider and provider.is_available():
                try:
                    return provider.generate_structured(request, schema)
                except Exception as e:
                    logger.error(f"Provider {provider_name} structured generation failed: {e}")
                    return self._try_fallback_structured(request, schema, provider_name)
            else:
                logger.warning(f"Provider {provider_name} not available, trying fallback")
                return self._try_fallback_structured(request, schema, provider_name)
        else:
            # Use primary provider with fallback
            return self._generate_structured_with_fallback(request, schema)
    
    def _generate_with_fallback(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Generate with primary provider and fallback to secondary"""
        # Try primary provider
        primary = self.providers.get(self.primary_provider)
        if primary and primary.is_available():
            try:
                return primary.generate(request)
            except Exception as e:
                logger.error(f"Primary provider {self.primary_provider} failed: {e}")
        
        # Try fallback provider
        fallback = self.providers.get(self.fallback_provider)
        if fallback and fallback.is_available():
            try:
                return fallback.generate(request)
            except Exception as e:
                logger.error(f"Fallback provider {self.fallback_provider} failed: {e}")
        
        # No providers available
        logger.error("No LLM providers available")
        return None
    
    def _generate_structured_with_fallback(self, request: LLMRequest, schema: Dict[str, Any]) -> Optional[LLMResponse]:
        """Generate structured response with fallback"""
        # Try primary provider
        primary = self.providers.get(self.primary_provider)
        if primary and primary.is_available():
            try:
                return primary.generate_structured(request, schema)
            except Exception as e:
                logger.error(f"Primary provider {self.primary_provider} structured generation failed: {e}")
        
        # Try fallback provider
        fallback = self.providers.get(self.fallback_provider)
        if fallback and fallback.is_available():
            try:
                return fallback.generate_structured(request, schema)
            except Exception as e:
                logger.error(f"Fallback provider {self.fallback_provider} structured generation failed: {e}")
        
        # No providers available
        logger.error("No LLM providers available for structured generation")
        return None
    
    def _try_fallback(self, request: LLMRequest, failed_provider: str) -> Optional[LLMResponse]:
        """Try other providers after a specific provider fails"""
        for name, provider in self.providers.items():
            if name != failed_provider and provider.is_available():
                try:
                    logger.info(f"Falling back to provider: {name}")
                    return provider.generate(request)
                except Exception as e:
                    logger.error(f"Fallback provider {name} also failed: {e}")
        
        return None
    
    def _try_fallback_structured(self, request: LLMRequest, schema: Dict[str, Any], 
                               failed_provider: str) -> Optional[LLMResponse]:
        """Try other providers for structured generation after a specific provider fails"""
        for name, provider in self.providers.items():
            if name != failed_provider and provider.is_available():
                try:
                    logger.info(f"Falling back to provider for structured generation: {name}")
                    return provider.generate_structured(request, schema)
                except Exception as e:
                    logger.error(f"Fallback provider {name} structured generation also failed: {e}")
        
        return None
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their status"""
        providers_info = []
        for name, provider in self.providers.items():
            try:
                info = provider.get_model_info()
                providers_info.append(info)
            except Exception as e:
                logger.error(f"Failed to get info for provider {name}: {e}")
                providers_info.append({
                    "provider": name,
                    "available": False,
                    "error": str(e)
                })
        
        return providers_info
    
    def is_any_provider_available(self) -> bool:
        """Check if any LLM provider is available"""
        for provider in self.providers.values():
            if provider.is_available():
                return True
        return False


# Singleton instance
llm_service = LLMService()