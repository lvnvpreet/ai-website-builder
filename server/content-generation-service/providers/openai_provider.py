import os
from typing import Dict, List, Any, Optional
from openai import OpenAI, AsyncOpenAI, OpenAIError
import tiktoken
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider."""
    
    def __init__(self, model_name: str = None):
        model_name = model_name or os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
        super().__init__(model_name)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.sync_client = OpenAI(api_key=api_key)
        
        # Get encoding for token counting
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding
            
        # Set maximum context size based on model
        self.context_sizes = {
            "gpt-4o": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385,
            "gpt-3.5-turbo-16k": 16385,
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpenAIError)
    )
    async def generate_content(self, prompt: str, max_tokens: Optional[int] = None, temperature: float = 0.7) -> str:
        """Generate content using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert website content creator. Create high-quality, engaging, and SEO-optimized content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            # Classify error for better handling
            if "rate limit" in str(e).lower():
                self.logger.warning("Rate limit hit, retrying...")
            elif "quota" in str(e).lower():
                self.logger.error("API quota exceeded")
            raise
    
    async def count_tokens(self, text: str) -> int:
        """Count tokens in the provided text using tiktoken."""
        return len(self.encoding.encode(text))
    
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        return "openai"
    
    def get_max_context_size(self) -> int:
        """Get the maximum context size for the model."""
        return self.context_sizes.get(self.model_name, 4096)  # Default to 4096