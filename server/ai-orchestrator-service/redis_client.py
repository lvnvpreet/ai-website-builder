import asyncio
import redis.asyncio as redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class RedisClient:
    def __init__(self, url=REDIS_URL):
        self.url = url
        self.client = None
        self.connected = False
        
    async def connect(self):
        """Connect to Redis."""
        if self.client is not None:
            return
            
        try:
            self.client = redis.from_url(self.url)
            # Test the connection
            await self.client.ping()
            self.connected = True
            print(f"Connected to Redis at {self.url}")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            self.client = None
            self.connected = False
            
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client is not None:
            await self.client.close()
            self.client = None
            self.connected = False
            
    async def get(self, key):
        """Get a value from Redis."""
        if not self.connected:
            await self.connect()
            
        if self.client is None:
            return None
            
        return await self.client.get(key)
        
    async def set(self, key, value, ex=None):
        """Set a value in Redis with optional expiry."""
        if not self.connected:
            await self.connect()
            
        if self.client is None:
            return False
            
        if ex is not None:
            return await self.client.set(key, value, ex=ex)
        return await self.client.set(key, value)
        
    async def zadd(self, key, mapping):
        """Add to a sorted set."""
        if not self.connected:
            await self.connect()
            
        if self.client is None:
            return 0
            
        return await self.client.zadd(key, mapping)