from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.logger = logging.getLogger(f"content_generation.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate_content(self, prompt: str, max_tokens: Optional[int] = None, temperature: float = 0.7) -> str:
        """Generate content from the LLM."""
        pass
    
    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Count tokens in the provided text."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        pass
    
    @abstractmethod
    def get_max_context_size(self) -> int:
        """Get the maximum context size for the model."""
        pass