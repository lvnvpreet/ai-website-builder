import os
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import requests # Import requests for Ollama
import json # Import json for Ollama payload
from typing import List, Dict, Any
from openai import OpenAI, OpenAIError # Import OpenAI client and error type
# from anthropic import Anthropic # Keep for potential future use

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Content Generation Service",
    description="Generates website content using LLMs based on user input and RAG context.",
    version="1.0.0"
)

# --- Configuration ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai") # Default to openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# ANTHROPIC_MODEL_NAME = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") # Default Ollama URL
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3") # Default Ollama model
# Add other provider configs as needed

# --- Initialize LLM Client (Only for providers that need a persistent client like OpenAI) ---
llm_client = None # For OpenAI, Anthropic etc.
try:
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        print(f"Initializing OpenAI client with model: {OPENAI_MODEL_NAME}")
        llm_client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized successfully.")
    elif LLM_PROVIDER == "ollama":
        print(f"LLM Provider set to Ollama. Using base URL: {OLLAMA_BASE_URL} and model: {OLLAMA_MODEL_NAME}")
        # No persistent client needed for Ollama with requests library
        pass
    # elif LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
        # print(f"Initializing Anthropic client with model: {ANTHROPIC_MODEL_NAME}")
        # llm_client = Anthropic(api_key=ANTHROPIC_API_KEY) # Uncomment when ready
        # print("Anthropic client initialized (placeholder).")
    # Add other providers here
    else:
        print(f"LLM Provider '{LLM_PROVIDER}' not configured or API key missing.")

except Exception as e:
    print(f"Error initializing LLM client: {e}")


# --- Data Models (Based on System Design) ---
# Input model might need refinement based on actual data flow from AI Orchestrator
class RagContextResult(BaseModel):
    documentId: str
    content: str
    similarity: float
    source: str | None = None

class GenerateContentInput(BaseModel):
    sessionId: str
    templateId: str # Chosen template
    processed_input: Dict[str, Any] # Data from Input Processing & Analysis phase
    rag_context: List[RagContextResult] = Field(default_factory=list) # Context from RAG
    branding: Dict[str, Any] | None = None # Colors, fonts, logo etc.

# Output model mirroring the design document
class SectionContent(BaseModel):
    id: str
    title: str
    content: str # Generated text/content for the section
    seoScore: float | None = None # Optional SEO score

class PageContent(BaseModel):
    type: str # e.g., 'homepage', 'about', 'contact'
    sections: List[SectionContent]

class GeneratedContentOutput(BaseModel):
    sessionId: str
    pages: List[PageContent]

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ Basic health check endpoint. """
    return {"message": "Content Generation Service is running!"}

@app.post("/generate-content", response_model=GeneratedContentOutput)
async def generate_content(data: GenerateContentInput):
    """
    Placeholder for content generation logic.
    Takes processed input, RAG context, template info, and branding,
    then uses an LLM to generate content structured for website pages/sections.
    """
    print(f"Received request to generate content for session: {data.sessionId}, template: {data.templateId}")
    print(f"Received RAG context items: {len(data.rag_context)}")

    generated_content = "Error: Content generation failed." # Default error message

    # --- Construct Prompt ---
    try:
        prompt_context = f"User Input Summary: {data.processed_input.get('summary', 'N/A')}\n"
        if data.rag_context:
            prompt_context += "Relevant Context:\n" + "\n".join([f"- {ctx.content}" for ctx in data.rag_context]) + "\n"
        prompt = f"Generate website content for a '{data.processed_input.get('industry', 'general')}' business based on the following:\n{prompt_context}\nGenerate a short welcome message for the homepage hero section."
    except Exception as e:
        print(f"Error constructing prompt: {e}")
        raise HTTPException(status_code=500, detail="Error constructing prompt.")

    # --- Call LLM based on Provider ---
    try:
        if LLM_PROVIDER == "openai":
            if not llm_client:
                raise HTTPException(status_code=503, detail="OpenAI client not available or configured (check API key).")
            print(f"Sending prompt to OpenAI (model: {OPENAI_MODEL_NAME})...")
            chat_completion = llm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful website content generator."},
                    {"role": "user", "content": prompt},
                ],
                model=OPENAI_MODEL_NAME,
            )
            generated_content = chat_completion.choices[0].message.content
            print(f"Received content from OpenAI: {generated_content[:100]}...")

        elif LLM_PROVIDER == "ollama":
            print(f"Sending prompt to Ollama (model: {OLLAMA_MODEL_NAME})...")
            ollama_url = f"{OLLAMA_BASE_URL}/api/chat"
            payload = {
                "model": OLLAMA_MODEL_NAME,
                "messages": [
                     {"role": "system", "content": "You are a helpful website content generator."},
                     {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            response = requests.post(ollama_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
            response.raise_for_status()
            response_data = response.json()
            generated_content = response_data.get("message", {}).get("content", "Error: Could not parse Ollama response.")
            print(f"Received content from Ollama: {generated_content[:100]}...")

        # elif LLM_PROVIDER == "anthropic":
            # Add Anthropic logic here, checking for its client
            # pass

        elif LLM_PROVIDER == "none":
            print("LLM_PROVIDER is 'none', returning placeholder content.")
            generated_content = "Placeholder content - LLM provider set to none."

        else:
             raise HTTPException(status_code=501, detail=f"LLM provider '{LLM_PROVIDER}' not supported.")

        # 3. TODO: Parse the LLM response into the PageContent/SectionContent structure
        # 4. TODO: Apply Design Rules Engine checks
        # 5. TODO: Handle errors, retries, content safety filtering

    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Ollama connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama connection error: {e}")
    except Exception as e:
        print(f"Error during LLM content generation: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating content: {e}")

    # --- Format Output (Using placeholder structure for now) ---
    placeholder_pages = [
        PageContent(type="homepage", sections=[
            SectionContent(id="hero", title="Welcome!", content=generated_content, seoScore=0.8),
            SectionContent(id="features", title="Our Features", content="Placeholder feature descriptions...", seoScore=0.7)
        ]),
        PageContent(type="about", sections=[
            SectionContent(id="mission", title="Our Mission", content="Placeholder mission statement...", seoScore=0.9)
        ])
    ]

    return GeneratedContentOutput(
        sessionId=data.sessionId,
        pages=placeholder_pages
    )

# --- Run the server (for local development) ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3009")) # Default port 3009
    print(f"Starting Content Generation Service on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
