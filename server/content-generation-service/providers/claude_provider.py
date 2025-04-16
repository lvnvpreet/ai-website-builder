import os
from typing import Dict, List, Any, Optional
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import LLMProvider

class ClaudeProvider(LLMProvider):
    """Claude implementation of LLM provider."""
    
    def __init__(self, model_name: str = None):
        model_name = model_name or os.getenv("CLAUDE_MODEL_NAME", "claude-3-opus-20240229")
        super().__init__(model_name)
        
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY environment variable is required")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
        # Set maximum context size based on model
        self.context_sizes = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 100000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000,
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(anthropic.APIError)
    )
    async def generate_content(self, prompt: str, max_tokens: Optional[int] = None, temperature: float = 0.7) -> str:
        """Generate content using Claude."""
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens or 4096,
                temperature=temperature,
                system="You are an expert website content creator. Create high-quality, engaging, and SEO-optimized content.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except anthropic.APIError as e:
            self.logger.error(f"Claude API error: {str(e)}")
            # Classify error for better handling
            if "rate" in str(e).lower():
                self.logger.warning("Rate limit hit, retrying...")
            raise
    
    async def count_tokens(self, text: str) -> int:
        """Approximate token count for Claude."""
        # Rough approximation: 1 token ≈ 4 chars for English text
        return len(text) // 4
    
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        return "claude"
    
    def get_max_context_size(self) -> int:
        """Get the maximum context size for the model."""
        return self.context_sizes.get(self.model_name, 100000)  # Default to 100k