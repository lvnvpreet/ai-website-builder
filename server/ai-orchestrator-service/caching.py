import json
from datetime import datetime
from typing import Any, Dict, Optional

class ResultCache:
    def __init__(self, redis_client, default_ttl=3600):
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.local_cache = {}  # Simple in-memory cache
        
    async def get(self, service_name, input_key):
        """Get result from cache (local or Redis)."""
        if self.redis_client is None:
            return None
            
        # Try local cache first
        local_key = f"{service_name}:{input_key}"
        if local_key in self.local_cache:
            return self.local_cache[local_key]
            
        # Try Redis cache
        redis_key = f"cache:{service_name}:{input_key}"
        try:
            cached_result = await self.redis_client.get(redis_key)
            if cached_result:
                result = json.loads(cached_result)
                # Update local cache
                self.local_cache[local_key] = result
                return result
        except Exception as e:
            print(f"Error getting from cache: {e}")
            
        return None
        
    async def set(self, service_name, input_key, result, ttl=None):
        """Set result in cache (both local and Redis)."""
        if self.redis_client is None:
            return
            
        try:
            # Set in Redis
            redis_key = f"cache:{service_name}:{input_key}"
            await self.redis_client.set(
                redis_key, 
                json.dumps(result),
                ex=ttl or self.default_ttl
            )
            
            # Update local cache
            local_key = f"{service_name}:{input_key}"
            self.local_cache[local_key] = result
        except Exception as e:
            print(f"Error setting cache: {e}")
    
    def generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate a consistent cache key from input data."""
        # Simple implementation - in production you might want something more sophisticated
        key_parts = []
        
        # Sort keys for consistent ordering
        for key in sorted(data.keys()):
            value = data[key]
            if isinstance(value, (str, int, float, bool)):
                key_parts.append(f"{key}:{value}")
            elif isinstance(value, (list, dict)):
                # Hash complex objects
                key_parts.append(f"{key}:{hash(str(value))}")
                
        return ":".join(key_parts)