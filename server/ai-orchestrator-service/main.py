import os
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
import httpx # For making async requests
# Import Pydantic models later for request/response validation
# from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="AI Orchestrator Service",
    description="Coordinates AI subsystems (Template Recommendation, RAG, Content Generation, Design Rules).",
    version="1.0.0"
)

# --- Configuration (Load URLs for dependent AI services) ---
# Example - replace with actual config loading if needed
TEMPLATE_RECOMMENDER_URL = os.getenv("TEMPLATE_RECOMMENDER_URL", "http://localhost:3007") # Example port
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:3008") # Example port
CONTENT_GENERATOR_URL = os.getenv("CONTENT_GENERATOR_URL", "http://localhost:3009") # Example port
DESIGN_RULES_URL = os.getenv("DESIGN_RULES_URL", "http://localhost:3010") # Example port


# --- Data Models (Example - Define based on actual needs) ---
# class OrchestrationInput(BaseModel):
#     processed_input: dict # Data from the Input Processing phase
#     sessionId: str

# class OrchestrationOutput(BaseModel):
#     website_generation_data: dict # Combined data ready for website generator

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ Basic health check endpoint. """
    return {"message": "AI Orchestrator Service is running!"}

# Example endpoint (replace with actual orchestration logic)
# @app.post("/orchestrate", response_model=OrchestrationOutput)
# async def orchestrate_ai_process(data: OrchestrationInput):
#     """
#     Placeholder for orchestrating the AI process.
#     Calls Template Recommender, RAG, Content Generator, Design Rules Validator.
#     """
#     print(f"Received request to orchestrate for session: {data.sessionId}")
#     # TODO: Implement calls to downstream AI services using httpx.AsyncClient
#     # TODO: Handle potential errors and retries
#     # TODO: Combine results

#     # Placeholder response
#     return OrchestrationOutput(website_generation_data={"status": "orchestration_placeholder"})


# --- Run the server (for local development) ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3011")) # Default to port 3011 for orchestrator
    print(f"Starting AI Orchestrator Service on http://localhost:{port}")
    # Use reload=True for development
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
