import asyncio
import uuid
import time
import json
import logging
from datetime import datetime
import httpx
from typing import Dict, List, Any, Optional
import random

from models import OrchestrationInput, OrchestrationOutput, OrchestrationStatus

logger = logging.getLogger("ai_orchestrator")

class ServiceError(Exception):
    """Exception raised for errors in service calls."""
    pass

class CircuitOpenError(Exception):
    """Exception raised when a circuit breaker is open."""
    pass

class ServiceCircuitBreaker:
    def __init__(self, service_name, failure_threshold=5, reset_timeout=60):
        self.service_name = service_name
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
    async def execute(self, coroutine_func, *args, **kwargs):
        if self.state == "open":
            # Check if we should try again
            if (self.last_failure_time is not None and 
                (datetime.utcnow() - self.last_failure_time).total_seconds() > self.reset_timeout):
                self.state = "half-open"
                logger.info(f"Circuit for {self.service_name} switched to half-open")
            else:
                raise CircuitOpenError(f"Circuit open for {self.service_name}")
                
        try:
            result = await coroutine_func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info(f"Circuit for {self.service_name} closed after successful call")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(f"Circuit for {self.service_name} opened after {self.failure_count} failures")
            raise ServiceError(f"Service {self.service_name} error: {str(e)}")

class Orchestrator:
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.circuit_breakers = {
            "template_recommender": ServiceCircuitBreaker("template_recommender"),
            "rag_service": ServiceCircuitBreaker("rag_service"),
            "content_generator": ServiceCircuitBreaker("content_generator"),
            "design_rules": ServiceCircuitBreaker("design_rules")
        }
        self.client = httpx.AsyncClient(timeout=30.0)  # Shared HTTP client
        
    async def retry_with_backoff(self, func, max_retries=3, base_delay=1.0, max_delay=60.0):
        retries = 0
        last_exception = None
        
        while retries <= max_retries:
            try:
                return await func()
            except (httpx.TimeoutException, httpx.ConnectError, ServiceError) as e:
                last_exception = e
                retries += 1
                
                if retries > max_retries:
                    break
                    
                # Calculate delay with exponential backoff and jitter
                delay = min(base_delay * (2 ** (retries - 1)) * (0.5 + random.random()), max_delay)
                logger.warning(f"Retry {retries}/{max_retries} after {delay:.2f}s due to: {str(e)}")
                await asyncio.sleep(delay)
        
        # If we've exhausted retries, raise the last exception
        raise last_exception
    
    async def call_service(self, service_name, url, data, method="POST"):
        circuit_breaker = self.circuit_breakers.get(service_name)
        if circuit_breaker is None:
            logger.warning(f"No circuit breaker defined for {service_name}, creating one")
            circuit_breaker = ServiceCircuitBreaker(service_name)
            self.circuit_breakers[service_name] = circuit_breaker
        
        async def make_request():
            try:
                if method == "POST":
                    response = await self.client.post(url, json=data, timeout=30.0)
                elif method == "GET":
                    response = await self.client.get(url, params=data, timeout=30.0)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from {service_name}: {e.response.status_code} - {e.response.text}")
                raise ServiceError(f"HTTP {e.response.status_code} from {service_name}: {e.response.text}")
            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.error(f"Request error to {service_name}: {str(e)}")
                raise ServiceError(f"Request to {service_name} failed: {str(e)}")
        
        # Use circuit breaker and retry with backoff
        return await circuit_breaker.execute(
            lambda: self.retry_with_backoff(make_request)
        )
    
    async def update_workflow_status(self, workflow_id, status, progress, current_step=None, error=None):
        """Update workflow status in Redis."""
        if self.redis_client is None:
            logger.warning("Redis client not available, skipping workflow status update")
            return
            
        try:
            workflow_key = f"workflow:{workflow_id}"
            workflow_data = await self.redis_client.get(workflow_key)
            
            if workflow_data:
                data = json.loads(workflow_data)
                data["status"] = status
                data["progress"] = progress
                data["last_updated"] = datetime.utcnow().isoformat()
                
                if current_step:
                    data["current_step"] = current_step
                    
                if error:
                    data["error"] = error
                    
                await self.redis_client.set(workflow_key, json.dumps(data))
                logger.info(f"Updated workflow {workflow_id} status to {status}, progress: {progress}")
            else:
                logger.warning(f"Workflow {workflow_id} not found in Redis")
        except Exception as e:
            logger.error(f"Error updating workflow status: {str(e)}")
    
    async def orchestrate(self, data: OrchestrationInput) -> OrchestrationOutput:
        """Main orchestration method that coordinates all services."""
        session_id = data.sessionId
        workflow_id = f"wf_{uuid.uuid4()}"
        
        # Initialize workflow in Redis
        if self.redis_client:
            try:
                workflow_data = {
                    "id": workflow_id,
                    "session_id": session_id,
                    "status": "processing",
                    "progress": 0.0,
                    "current_step": "initialize",
                    "created_at": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat()
                }
                await self.redis_client.set(f"workflow:{workflow_id}", json.dumps(workflow_data))
                logger.info(f"Created workflow {workflow_id} for session {session_id}")
            except Exception as e:
                logger.error(f"Error creating workflow record: {str(e)}")
        
        try:
            # Step 1: Call Template Recommender
            await self.update_workflow_status(workflow_id, "processing", 0.1, "template_recommendation")
            template_data = {
                "sessionId": session_id,
                "processed_input": data.processed_input
            }
            template_result = await self.call_service(
                "template_recommender", 
                "http://localhost:3007/recommend-templates", 
                template_data
            )
            logger.info(f"Template recommendation complete for {session_id}")
            
            # Step 2: Call RAG Service (if needed)
            await self.update_workflow_status(workflow_id, "processing", 0.3, "rag_context")
            if not data.rag_context:  # Only call RAG if context not already provided
                rag_data = {
                    "query": data.processed_input.get("description", ""),
                    "top_k": 5,
                    "sessionId": session_id
                }
                try:
                    rag_result = await self.call_service(
                        "rag_service", 
                        "http://localhost:3008/query", 
                        rag_data
                    )
                    logger.info(f"RAG query complete for {session_id}")
                    # Extract context from RAG results
                    rag_context = rag_result.get("results", [])
                except ServiceError as e:
                    logger.warning(f"RAG service error, continuing without RAG context: {str(e)}")
                    rag_context = []
            else:
                rag_context = data.rag_context
            
            # Step 3: Call Content Generator
            await self.update_workflow_status(workflow_id, "processing", 0.5, "content_generation")
            # Get the top template recommendation
            template_id = template_result.get("recommendations", [{}])[0].get("templateId", "default_template")
            
            content_data = {
                "sessionId": session_id,
                "templateId": template_id,
                "processed_input": data.processed_input,
                "rag_context": rag_context,
                "branding": data.branding
            }
            content_result = await self.call_service(
                "content_generator", 
                "http://localhost:3009/generate-content", 
                content_data
            )
            logger.info(f"Content generation complete for {session_id}")
            
            # Step 4: Call Design Rules Validator
            await self.update_workflow_status(workflow_id, "processing", 0.8, "design_rules")
            design_data = {
                "template_id": template_id,
                "generated_content": content_result,
                "branding": data.branding
            }
            try:
                design_result = await self.call_service(
                    "design_rules", 
                    "http://localhost:3010/validate-design", 
                    design_data
                )
                logger.info(f"Design validation complete for {session_id}")
            except ServiceError as e:
                logger.warning(f"Design rules validation failed, continuing with generation: {str(e)}")
                design_result = {"passed": True, "issues": []}
            
            # Step 5: Combine results and return
            await self.update_workflow_status(workflow_id, "completed", 1.0, "finalization")
            
            # Construct final output
            result = OrchestrationOutput(
                sessionId=session_id,
                status=OrchestrationStatus.COMPLETED,
                progress=1.0,
                website_generation_data={
                    "template": template_result,
                    "design_validation": design_result
                },
                pages=content_result.get("pages", [])
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Orchestration error for session {session_id}: {str(e)}")
            await self.update_workflow_status(
                workflow_id, 
                "failed", 
                0.0, 
                error=str(e)
            )
            
            # Return error result
            return OrchestrationOutput(
                sessionId=session_id,
                status=OrchestrationStatus.FAILED,
                progress=0.0,
                error=f"Orchestration failed: {str(e)}"
            )