import os
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel, Field
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
# Add other provider configs as needed

# --- Initialize LLM Client ---
llm_client = None
try:
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        print(f"Initializing OpenAI client with model: {OPENAI_MODEL_NAME}")
        llm_client = OpenAI(api_key=OPENAI_API_KEY) # Initialize the actual client
        print("OpenAI client initialized successfully.")
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

    if llm_client is None:
         # If no client is configured (e.g., missing API key), raise error
         # unless explicitly set to "none" for testing without LLM.
         if LLM_PROVIDER != "none":
             raise HTTPException(status_code=503, detail=f"LLM client ({LLM_PROVIDER}) not available or configured.")
         else:
             # Handle "none" provider case - return placeholder or error? For now, placeholder.
             print("LLM_PROVIDER is 'none', returning placeholder content.")
             generated_content = "Placeholder content - LLM provider set to none."
             # Fall through to return placeholder structure
    else:
        # --- Actual LLM Call Logic ---
        try:
            # 1. Construct a simple prompt (Refine this significantly later)
            prompt_context = f"User Input Summary: {data.processed_input.get('summary', 'N/A')}\n"
            if data.rag_context:
                prompt_context += "Relevant Context:\n" + "\n".join([f"- {ctx.content}" for ctx in data.rag_context]) + "\n"
            prompt = f"Generate website content for a '{data.processed_input.get('industry', 'general')}' business based on the following:\n{prompt_context}\nGenerate a short welcome message for the homepage hero section."

            print(f"Sending prompt to {LLM_PROVIDER} (model: {OPENAI_MODEL_NAME})...")

            # 2. Call the LLM
            # Example using OpenAI chat completions API
            chat_completion = llm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful website content generator."},
                    {"role": "user", "content": prompt},
                ],
                model=OPENAI_MODEL_NAME,
                # Add other parameters like max_tokens, temperature as needed
            )
            generated_content = chat_completion.choices[0].message.content
            print(f"Received content from LLM: {generated_content[:100]}...")

            # 3. TODO: Parse the LLM response into the PageContent/SectionContent structure
            # 4. TODO: Apply Design Rules Engine checks
            # 5. TODO: Handle errors, retries, content safety filtering

        except OpenAIError as e: # Catch specific OpenAI errors
            print(f"OpenAI API error: {e}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")
        except Exception as e: # Catch other potential errors
            print(f"Error during LLM content generation: {e}")
            raise HTTPException(status_code=500, detail="Error generating content.")

    # --- Format Output (Using placeholder structure for now) ---
    # Replace this with actual parsed content from the LLM response later
    placeholder_pages = [
        PageContent(type="homepage", sections=[
            SectionContent(id="hero", title="Welcome!", content=generated_content if llm_client else "Placeholder - LLM not configured", seoScore=0.8),
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
