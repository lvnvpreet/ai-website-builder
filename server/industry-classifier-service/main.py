import os
import os
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from transformers import pipeline # Import pipeline
import torch # Import torch

# Load environment variables from .env file
load_dotenv()

# --- Load Zero-Shot Classification Pipeline ---
# Using a model suitable for NLI/Zero-Shot, like BART MNLI.
# This avoids needing a model fine-tuned on specific industry labels initially.
MODEL_NAME = "facebook/bart-large-mnli"
classifier_pipeline = None

try:
    print(f"Loading zero-shot classification pipeline with model: {MODEL_NAME}...")
    # No need to load model/tokenizer separately for pipeline
    classifier_pipeline = pipeline("zero-shot-classification", model=MODEL_NAME)
    print("Zero-shot classification pipeline loaded successfully.")
except Exception as e:
    print(f"Error loading zero-shot pipeline: {e}")
    # Handle appropriately if loading fails

app = FastAPI(
    title="Industry Classifier Service",
    description="Classifies business type based on input using zero-shot learning.",
    version="1.0.0"
)

# --- Candidate Labels (Example - Should be configurable or more extensive) ---
DEFAULT_INDUSTRY_LABELS = [
    "technology", "software", "hardware", "e-commerce", "retail",
    "finance", "fintech", "banking", "insurance",
    "healthcare", "medical", "pharmaceutical",
    "education", "edtech",
    "real estate", "construction",
    "food service", "restaurant", "hospitality",
    "manufacturing", "automotive",
    "energy", "utilities",
    "media", "entertainment", "publishing",
    "non-profit", "government"
]


# --- Data Models ---
class ClassificationInput(BaseModel):
    business_description: str
    candidate_labels: list[str] | None = None # Allow overriding default labels
    sessionId: str | None = None # Optional

class ClassificationOutput(BaseModel):
    industry_code: str
    confidence_score: float
    related_industries: list[str] = []

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ Basic health check endpoint. """
    return {"message": "Industry Classifier Service is running!"}

# Endpoint for industry classification
@app.post("/classify", response_model=ClassificationOutput)
async def classify_industry(data: ClassificationInput):
    """
    Classifies the industry based on the business description using zero-shot classification.
    """
    if not classifier_pipeline:
         raise HTTPException(status_code=503, detail="Classifier pipeline not loaded.")

    print(f"Received description for classification: {data.business_description[:50]}...")

    candidate_labels = data.candidate_labels or DEFAULT_INDUSTRY_LABELS
    print(f"Using candidate labels: {candidate_labels[:5]}...") # Log first few

    try:
        # Perform zero-shot classification
        # The pipeline returns labels sorted by score
        results = classifier_pipeline(data.business_description, candidate_labels=candidate_labels, multi_label=False) # Assuming single best label needed

        top_label = results['labels'][0]
        top_score = results['scores'][0]
        # Use other results as 'related' - adjust as needed
        related_industries = results['labels'][1:4] # Example: next top 3

        print(f"Classification result: {top_label} (Score: {top_score:.4f})")

        return ClassificationOutput(
            industry_code=top_label, # Use the predicted label directly
            confidence_score=top_score,
            related_industries=related_industries
        )
    except Exception as e:
        print(f"Error during zero-shot classification inference: {e}")
        raise HTTPException(status_code=500, detail="Error during classification inference.")

# --- Run the server (for local development) ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3005")) # Default to port 3005
    print(f"Starting Industry Classifier Service on http://localhost:{port}")
    # Use reload=True for development
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
