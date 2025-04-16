import os
import json
from typing import Dict, List, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMProvider

class OllamaProvider(LLMProvider):
    """Ollama implementation of LLM provider."""
    
    def __init__(self, model_name: str = None):
        model_name = model_name or os.getenv("OLLAMA_MODEL_NAME", "llama3")
        super().__init__(model_name)
        
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")
        
        # Set maximum context size based on model
        # These are estimates, could vary by specific model version
        self.context_sizes = {
            "llama3": 8192,
            "llama2": 4096,
            "mistral": 8192,
            "gemma": 8192,
            "mixtral": 32768,
            "phi": 2048,
            "deepseek-coder": 16384,
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_content(self, prompt: str, max_tokens: Optional[int] = None, temperature: float = 0.7) -> str:
        """Generate content using Ollama."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"You are an expert website content creator. Create high-quality, engaging, and SEO-optimized content.\n\n{prompt}",
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens if max_tokens else 2048,
                        }
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except httpx.HTTPError as e:
            self.logger.error(f"Ollama API error: {str(e)}")
            raise
    
    async def count_tokens(self, text: str) -> int:
        """Approximate token count for Ollama models."""
        # Rough approximation: 1 token ≈ 4 chars for English text
        return len(text) // 4
    
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        return "ollama"
    
    def get_max_context_size(self) -> int:
        """Get the maximum context size for the model."""
        # Extract base model name by removing version numbers
        base_model = self.model_name.split(':')[0]
        
        # Check if base model exists in context sizes
        for model_prefix, size in self.context_sizes.items():
            if base_model.startswith(model_prefix):
                return size
                
        return 4096  # Default to 4096 if unknown