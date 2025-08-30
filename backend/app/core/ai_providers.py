"""
AI Provider abstraction layer supporting multiple LLM providers.
Supports OpenAI (GPT-4o, GPT-4-turbo) and Anthropic (Claude 3.5 Sonnet).
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import structlog
from app.config import settings

logger = structlog.get_logger()


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a completion from the AI model"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider supporting GPT-4o and GPT-4-turbo"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.client = None
        
        if api_key:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        if not self.client:
            raise ValueError("OpenAI client not initialized - missing API key")
        
        try:
            # Build request parameters
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            # Only add max_tokens if specified
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            
            response = await self.client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI completion failed: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider supporting Claude 3.5 Sonnet"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
        self.client = None
        
        if api_key:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        if not self.client:
            raise ValueError("Claude client not initialized - missing API key")
        
        try:
            # Convert OpenAI format to Claude format
            system_message = None
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Build request parameters
            params = {
                "model": self.model,
                "system": system_message if system_message else "",
                "messages": claude_messages,
                "temperature": temperature
            }
            
            # Claude requires max_tokens, use a high default if not specified
            params["max_tokens"] = max_tokens if max_tokens is not None else 4096
            
            response = await self.client.messages.create(**params)
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude completion failed: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model


class AIProviderFactory:
    """Factory to create the appropriate AI provider based on configuration"""
    
    @staticmethod
    def create_provider() -> Optional[AIProvider]:
        """
        Create an AI provider based on environment configuration.
        Priority: CLAUDE_API_KEY > OPENAI_API_KEY
        """
        
        # Check for Claude API key first (newest, best for analysis)
        claude_api_key = getattr(settings, 'CLAUDE_API_KEY', None)
        if claude_api_key and len(claude_api_key) > 10:  # Check for actual key, not empty string
            model = getattr(settings, 'CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
            logger.info(f"Using Claude provider with model: {model}")
            return ClaudeProvider(api_key=claude_api_key, model=model)
        
        # Fall back to OpenAI
        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if openai_api_key and len(openai_api_key) > 10:  # Check for actual key, not empty string
            # Use newer models by default
            model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o')
            
            # Map old model names to new ones
            model_mapping = {
                'gpt-4': 'gpt-4o',
                'gpt-4-turbo-preview': 'gpt-4-turbo',
                'gpt-4-1106-preview': 'gpt-4-turbo',
                'gpt-3.5-turbo': 'gpt-4o-mini'  # Upgrade to better mini model
            }
            
            if model in model_mapping:
                logger.info(f"Upgrading model from {model} to {model_mapping[model]}")
                model = model_mapping[model]
            
            logger.info(f"Using OpenAI provider with model: {model}")
            return OpenAIProvider(api_key=openai_api_key, model=model)
        
        logger.warning("No AI provider configured - add CLAUDE_API_KEY or OPENAI_API_KEY to .env")
        return None


# Available models for reference
AVAILABLE_MODELS = {
    "openai": [
        "gpt-4o",           # Latest and most capable (Nov 2024)
        "gpt-4o-mini",      # Faster, cheaper alternative
        "gpt-4-turbo",      # Previous turbo model
        "gpt-4",            # Original GPT-4
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022",  # Latest Claude 3.5 Sonnet (Oct 2024)
        "claude-3-opus-20240229",       # Most capable but slower
        "claude-3-sonnet-20240229",     # Balanced
        "claude-3-haiku-20240307",      # Fastest
    ]
}