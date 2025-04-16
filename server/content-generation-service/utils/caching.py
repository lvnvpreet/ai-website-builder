import json
import hashlib
from typing import Dict, Any, Optional
import asyncio
import os
import redis.asyncio as redis
from datetime import datetime

class ContentCache:
    """Caching utility for content generation."""
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.ttl = int(os.getenv("CACHE_TTL", "3600"))  # Default 1 hour
        self.cache_enabled = redis_url is not None
        self.redis = None
        
        if self.cache_enabled:
            try:
                self.redis = redis.from_url(redis_url)
            except Exception as e:
                print(f"Error connecting to Redis: {e}")
                self.cache_enabled = False
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get content from cache."""
        if not self.cache_enabled or not self.redis:
            return None
            
        try:
            data = await self.redis.get(f"content:{key}")
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Error getting from cache: {e}")
        
        return None
    
    async def set(self, key: str, data: Dict[str, Any]) -> bool:
        """Set content in cache."""
        if not self.cache_enabled or not self.redis:
            return False
            
        try:
            await self.redis.set(f"content:{key}", json.dumps(data), ex=self.ttl)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    def generate_key(self, data: Dict[str, Any]) -> str:
        """Generate a cache key from the input data."""
        # Extract key fields that would affect generation
        key_data = {
            "templateId": data.get("templateId", ""),
            "industry": data.get("processed_input", {}).get("industry", ""),
            "business_name": data.get("processed_input", {}).get("business_name", ""),
            "description": data.get("processed_input", {}).get("description", "")[:100],  # Use first 100 chars for shorter key
        }
        
        # Add first RAG context if present
        if data.get("rag_context") and len(data["rag_context"]) > 0:
            key_data["rag"] = data["rag_context"][0].get("content", "")[:50]
            
        # Serialize and hash
        serialized = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(serialized.encode('utf-8')).hexdigest()