import os
import spacy # Import spacy
import textstat # Import textstat
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel # Import Pydantic

# Load environment variables from .env file
load_dotenv()

# Load the spaCy English model
# Consider loading a larger model if more detailed analysis is needed later
try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model 'en_core_web_sm' loaded successfully.")
except OSError:
    print("Could not find spaCy model 'en_core_web_sm'.")
    print("Download it by running: python -m spacy download en_core_web_sm")
    nlp = None

app = FastAPI(
    title="SEO Analyzer Service",
    description="Analyzes text for SEO metrics like keyword density, readability, and generates meta tags.",
    version="1.0.0"
)

# --- Data Models (Example - Define based on actual needs) ---
class SeoInput(BaseModel):
    text: str
    target_keywords: list[str] | None = None # Optional target keywords
    sessionId: str | None = None # Optional

class SeoOutput(BaseModel):
    readability_score: float | None = None # e.g., Flesch Reading Ease
    keyword_density: dict[str, float] = {} # Density for target keywords
    meta_description: str | None = None # Suggested meta description
    meta_keywords: list[str] = [] # Suggested meta keywords

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ Basic health check endpoint. """
    return {"message": "SEO Analyzer Service is running!"}

# Endpoint for SEO analysis
@app.post("/seo", response_model=SeoOutput)
async def analyze_seo(data: SeoInput):
    """
    Analyzes text for readability, keyword density, and generates basic meta tags.
    """
    if nlp is None:
        raise HTTPException(status_code=503, detail="spaCy language model not loaded.")

    print(f"Received text for SEO analysis: {data.text[:50]}...")

    readability_score = None
    keyword_density_output = {}
    meta_description_output = None
    meta_keywords_output = []

    try:
        doc = nlp(data.text) # Process text once for all analyses

        # Calculate readability score
        readability_score = textstat.flesch_reading_ease(data.text)
        print(f"Calculated Flesch Reading Ease: {readability_score}")

        # Calculate keyword density (if target keywords provided)
        if data.target_keywords:
             text_lower = data.text.lower()
             total_words = len([token for token in doc if not token.is_punct])
             if total_words > 0:
                 for keyword in data.target_keywords:
                     keyword_lower = keyword.lower()
                     count = text_lower.count(keyword_lower) # Simple count
                     keyword_density_output[keyword] = round(count / total_words, 4) if total_words > 0 else 0
             print(f"Calculated Keyword Density: {keyword_density_output}")

        # Generate Meta Description (e.g., first sentence)
        try:
            first_sentence = next(doc.sents).text.strip()
            max_desc_len = 160 # Typical max length for meta descriptions
            if len(first_sentence) > max_desc_len:
                 # Find last space before limit
                 last_space = first_sentence[:max_desc_len].rfind(' ')
                 if last_space != -1:
                     meta_description_output = first_sentence[:last_space] + "..."
                 else: # No space found, just truncate hard
                     meta_description_output = first_sentence[:max_desc_len-3] + "..."
            else:
                 meta_description_output = first_sentence
            print(f"Generated Meta Description: {meta_description_output}")
        except StopIteration:
            # Fallback if no sentences found (e.g., very short text)
            meta_description_output = data.text[:160]
            print("Could not find sentence boundary, using truncated text for meta description.")

        # Generate Meta Keywords (non-stopword nouns/proper nouns lemmas)
        meta_keywords_output = list(set(
            token.lemma_.lower()
            for token in doc
            if not token.is_stop and not token.is_punct and token.pos_ in ["NOUN", "PROPN"]
        ))
        print(f"Generated Meta Keywords: {meta_keywords_output[:10]}...") # Log first few

        # Return results
        return SeoOutput(
            readability_score=readability_score,
            keyword_density=keyword_density_output,
            meta_description=meta_description_output,
            meta_keywords=meta_keywords_output
        )

    except Exception as e:
        print(f"Error during SEO analysis: {e}")
        # Return partial results if possible, or raise error
        # For now, just return placeholders if score calculation failed but others might work
        # A more robust implementation might return only the successful parts
        return SeoOutput(
            readability_score=readability_score, # Might be None if error occurred before calculation
            keyword_density=keyword_density_output, # Might be empty
            meta_description=meta_description_output, # Might be None or fallback
            meta_keywords=meta_keywords_output # Might be empty
        )
        # Alternatively, raise HTTPException for any error:
        # raise HTTPException(status_code=500, detail=f"Error during SEO analysis: {e}")

# --- Run the server (for local development) ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3006")) # Default to port 3006
    print(f"Starting SEO Analyzer Service on http://localhost:{port}")
    # Use reload=True for development
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
