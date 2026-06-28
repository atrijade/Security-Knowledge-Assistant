from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from config import get_config
from src.embeddings.model import SentenceTransformerEmbedder
from src.llm.client import LLMConfigurationError, LLMRequest, GeminiLLMClient
from src.llm.prompting import build_context_block
from src.retrieval.service import RetrievalService
from src.vectordb.chroma_store import ChromaVectorStore
from google.genai.errors import APIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vulnerability Management RAG API")

# Add CORS Middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.post("/api/query")
async def api_query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
        
    try:
        config = get_config()
        
        # 1. Retrieval
        embedder = SentenceTransformerEmbedder(config.embedding_model_name)
        store = ChromaVectorStore(config.vector_db_dir, config.chroma_collection_name)
        retrieval_service = RetrievalService(embedder, store)
        retrieval = retrieval_service.retrieve(request.question, config.top_k)
        
        # 2. Build Context
        context = build_context_block(retrieval)
        
        # 3. LLM Call
        llm_client = GeminiLLMClient(
            api_key=config.llm_api_key,
            model_name=config.llm_model_name,
            temperature=config.llm_temperature,
        )
        answer = llm_client.answer(LLMRequest(question=request.question, context=context))
        
        # 4. Format Chunks for API response
        formatted_chunks = []
        for chunk in retrieval.chunks:
            formatted_chunks.append({
                "source": chunk.metadata.get("source_filename", "unknown"),
                "chunk_id": chunk.metadata.get("chunk_id", "unknown"),
                "distance": chunk.distance if chunk.distance is not None else 0.0,
                "text": chunk.text
            })
            
        return {
            "answer": answer,
            "chunks": formatted_chunks
        }
        
    except APIError as exc:
        logger.error("Gemini API Error: %s", exc)
        message = str(exc)
        if hasattr(exc, "message") and exc.message:
            message = exc.message
        elif isinstance(exc, tuple) and len(exc) > 1 and isinstance(exc[1], dict):
            err_dict = exc[1].get("error", {})
            message = err_dict.get("message", message)
        raise HTTPException(status_code=502, detail=f"Gemini API Call Exceeded/Error: {message}")
    except LLMConfigurationError as exc:
        logger.error("Configuration Error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("An unexpected error occurred during query execution")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
