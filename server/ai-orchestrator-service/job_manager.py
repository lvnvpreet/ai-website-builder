import uuid
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

class JobManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        
    async def enqueue_job(self, job_type, payload, priority=0):
        """Add a job to the queue."""
        if self.redis_client is None:
            return None
            
        job_id = f"job:{uuid.uuid4()}"
        job_data = {
            "id": job_id,
            "type": job_type,
            "status": "queued",
            "priority": priority,
            "payload": payload,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        try:
            # Add to appropriate queue based on priority
            queue_key = f"job_queue:{priority}"
            job_key = f"job:{job_id}"
            
            # Store job data
            await self.redis_client.set(job_key, json.dumps(job_data))
            # Add to queue (sorted set with priority)
            await self.redis_client.zadd(queue_key, {job_id: time.time()})
            
            return job_id
        except Exception as e:
            print(f"Error enqueueing job: {e}")
            return None
            
    async def get_job_status(self, job_id):
        """Get the status of a job."""
        if self.redis_client is None:
            return None
            
        try:
            job_key = f"job:{job_id}"
            job_data = await self.redis_client.get(job_key)
            
            if job_data:
                return json.loads(job_data)
            return None
        except Exception as e:
            print(f"Error getting job status: {e}")
            return None
            
    async def update_job_status(self, job_id, status, result=None, error=None):
        """Update the status of a job."""
        if self.redis_client is None:
            return False
            
        try:
            job_key = f"job:{job_id}"
            job_data = await self.redis_client.get(job_key)
            
            if job_data:
                data = json.loads(job_data)
                data["status"] = status
                data["updated_at"] = datetime.utcnow().isoformat()
                
                if result is not None:
                    data["result"] = result
                    
                if error is not None:
                    data["error"] = error
                    
                await self.redis_client.set(job_key, json.dumps(data))
                return True
            return False
        except Exception as e:
            print(f"Error updating job status: {e}")
            return False