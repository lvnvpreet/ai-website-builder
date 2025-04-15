import os
import spacy # Import spacy
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel # Import Pydantic

# Load environment variables from .env file
load_dotenv()

# Load the spaCy English model
try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model 'en_core_web_sm' loaded successfully.")
except OSError:
    print("Could not find spaCy model 'en_core_web_sm'.")
    print("Download it by running: python -m spacy download en_core_web_sm")
    # Depending on requirements, you might want to exit or handle this differently
    nlp = None # Set nlp to None if model loading fails

# Define the FastAPI app instance *once*
app = FastAPI(
    title="Metadata Extraction Service",
    description="Extracts entities, keywords, etc., from text.",
    version="1.0.0"
)

# --- Data Models ---
class ExtractionInput(BaseModel):
    text: str
    sessionId: str | None = None # Optional session ID for context

class EntityOutput(BaseModel):
    text: str
    label: str # spaCy entity label (e.g., ORG, PERSON, GPE)
    start_char: int
    end_char: int

class ExtractionOutput(BaseModel):
    entities: list[EntityOutput] = []
    keywords: list[str] = [] # Placeholder for keywords
    # Add other extracted metadata fields later

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ Basic health check endpoint. """
    return {"message": "Metadata Extraction Service is running!"}

# Endpoint for metadata extraction
@app.post("/extract", response_model=ExtractionOutput)
async def extract_metadata(data: ExtractionInput):
    """
    Extracts named entities from the input text using spaCy.
    Placeholder for keyword extraction.
    """
    if nlp is None:
        raise HTTPException(status_code=503, detail="spaCy language model not loaded.")

    print(f"Received text for extraction: {data.text[:50]}...") # Log snippet

    try:
        doc = nlp(data.text)

        # Extract entities
        entities_output = [
            EntityOutput(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char
            ) for ent in doc.ents
        ]

        # Extract keywords (simple approach: non-stopword nouns/proper nouns lemmas)
        keywords_output = list(set(
            token.lemma_.lower()
            for token in doc
            if not token.is_stop and not token.is_punct and token.pos_ in ["NOUN", "PROPN"]
        ))

        return ExtractionOutput(
            entities=entities_output,
            keywords=keywords_output
        )
    except Exception as e:
        print(f"Error during metadata extraction: {e}")
        raise HTTPException(status_code=500, detail="Error processing text for metadata extraction.")

# --- Run the server (for local development) ---
# This part is usually handled by uvicorn command line directly

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3004")) # Default to port 3004
    print(f"Starting Metadata Extraction Service on http://localhost:{port}")
    # Use reload=True for development to automatically reload on code changes
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
