import os
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone # Ensure ONLY Pinecone is imported here
from typing import List, Dict, Any

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST") # For Serverless indexes
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "ai-website-builder")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL_NAME") # Optional

# --- Initialize Embedding Model Only ---
embedding_model = None
try:
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(f"Embedding model '{EMBEDDING_MODEL_NAME}' loaded successfully.")
except Exception as e:
    print(f"CRITICAL: Error loading embedding model '{EMBEDDING_MODEL_NAME}': {e}")
    embedding_model = None

app = FastAPI(
    title="RAG Subsystem Service",
    description="Handles Retrieval-Augmented Generation tasks: querying vector DB, embedding, reranking.",
    version="1.0.0"
)

# --- Data Models ---
class RAGQueryInput(BaseModel):
    query: str
    top_k: int = 5
    sessionId: str | None = None

class RAGResult(BaseModel):
    documentId: str
    content: str
    similarity: float
    source: str | None = None

class RAGQueryOutput(BaseModel):
    query: str
    results: list[RAGResult] = []

# --- Global variable for Pinecone Index (initialized on first query) ---
pinecone_index_global = None
pinecone_init_error = None
pinecone_client_global = None

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ Basic health check endpoint. """
    global pinecone_init_error, pinecone_index_global
    status = {
        "message": "RAG Subsystem Service is running!",
        "embedding_model_loaded": embedding_model is not None,
        "pinecone_status": "Not initialized yet" if pinecone_index_global is None and pinecone_init_error is None else ("Initialized" if pinecone_index_global else f"Initialization Error: {pinecone_init_error}")
    }
    return status

@app.post("/query", response_model=RAGQueryOutput)
async def query_rag(data: RAGQueryInput):
    """
    Embeds query, searches vector DB, optionally reranks results.
    Initializes Pinecone connection on first call if needed.
    """
    global pinecone_index_global, pinecone_init_error, pinecone_client_global

    print(f"Received RAG query: {data.query[:50]}...")

    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model not loaded.")

    # --- Initialize Pinecone on first query if not already done ---
    if pinecone_index_global is None and pinecone_init_error is None:
        if PINECONE_API_KEY and PINECONE_INDEX_NAME and PINECONE_INDEX_HOST:
            try:
                print("Attempting Pinecone initialization on first query...")
                if pinecone_client_global is None:
                     print("Initializing Pinecone client...")
                     pinecone_client_global = Pinecone(api_key=PINECONE_API_KEY)

                print(f"Attempting to get index object for host: {PINECONE_INDEX_HOST}...")
                pinecone_index_global = pinecone_client_global.Index(host=PINECONE_INDEX_HOST)
                stats = pinecone_index_global.describe_index_stats()
                print(f"Successfully connected to Pinecone index '{PINECONE_INDEX_NAME}'. Stats: {stats}")
            except Exception as e:
                pinecone_init_error = str(e)
                print(f"Error initializing/connecting to Pinecone: {pinecone_init_error}")
                pinecone_index_global = None
        else:
            pinecone_init_error = "API Key, Index Name, or Host missing in environment variables."
            print(f"Pinecone initialization skipped: {pinecone_init_error}")
            pinecone_index_global = None

    # --- Proceed with query if Pinecone is available ---
    current_pinecone_index = pinecone_index_global

    if current_pinecone_index is None:
         print(f"Pinecone not available. Reason: {pinecone_init_error}")
         return RAGQueryOutput(query=data.query, results=[])

    try:
        # 1. Embed the query
        query_vector = embedding_model.encode(data.query).tolist()
        print(f"Generated query vector (first 5 dims): {query_vector[:5]}...")

        # 2. Query Vector DB
        db_results = []
        try:
            print(f"Querying Pinecone index '{PINECONE_INDEX_NAME}' with top_k={data.top_k}...")
            response = current_pinecone_index.query(
                vector=query_vector,
                top_k=data.top_k,
                include_metadata=True
            )
            db_results = [
                {"id": match.id, "score": match.score, "metadata": match.metadata or {}}
                for match in response.get('matches', [])
            ]
            print(f"Pinecone search returned {len(db_results)} results.")
        except Exception as query_e: # Catch any exception during query
            print(f"Error querying Pinecone index: {query_e}")
            raise HTTPException(status_code=500, detail=f"Error querying vector database: {query_e}")

        # 3. TODO: Rerank results using reranker_model (optional)
        final_results = db_results

        # 4. Format results
        formatted_results = [
            RAGResult(
                documentId=res["id"],
                content=res["metadata"].get("text", ""),
                similarity=res["score"],
                source=res["metadata"].get("source")
            ) for res in final_results
        ]

        return RAGQueryOutput(
            query=data.query,
            results=formatted_results
        )

    except Exception as e:
        print(f"Error during RAG query processing: {e}")
        raise HTTPException(status_code=500, detail="Error processing RAG query.")

# --- Run the server (for local development) ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3008"))
    print(f"Starting RAG Subsystem Service on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
