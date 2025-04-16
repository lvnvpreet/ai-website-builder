from typing import Dict, Optional
import os
import logging
from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .ollama_provider import OllamaProvider

logger = logging.getLogger("content_generation.providers")

def get_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """Get the LLM provider based on environment variable or explicit name."""
    provider_name = provider_name or os.getenv("LLM_PROVIDER", "openai").lower()
    
    logger.info(f"Initializing LLM provider: {provider_name}")
    
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "claude":
        return ClaudeProvider()
    elif provider_name == "ollama":
        return OllamaProvider()
    else:
        logger.warning(f"Unknown provider '{provider_name}', defaulting to OpenAI")
        return OpenAIProvider()