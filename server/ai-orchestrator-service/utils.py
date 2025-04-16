import logging
import json
import time
from contextvars import ContextVar
from fastapi import Request

# Context variables for request tracking
request_id_var = ContextVar("request_id", default=None)
session_id_var = ContextVar("session_id", default=None)

# Structured logging setup
class CustomJSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add context from record
        for key, value in getattr(record, "context", {}).items():
            log_record[key] = value
            
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging():
    """Configure structured logging."""
    logger = logging.getLogger("ai_orchestrator")
    # Remove existing handlers if any
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
            
    handler = logging.StreamHandler()
    handler.setFormatter(CustomJSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

async def check_service_health(url):
    """Check if a service is healthy."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/", timeout=5.0)
            if response.status_code == 200:
                return {"status": "healthy"}
            return {"status": "degraded", "status_code": response.status_code}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}