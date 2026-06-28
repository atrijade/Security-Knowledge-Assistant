from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv



@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    data_dir: Path
    vector_db_dir: Path
    manifest_path: Path
    chroma_collection_name: str
    embedding_model_name: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    llm_model_name: str
    llm_api_key: str | None
    llm_temperature: float


def get_config() -> AppConfig:
    load_dotenv()
    project_root = Path(__file__).resolve().parent
    data_dir = Path(os.getenv("RAG_DATA_DIR", project_root / "data"))
    vector_db_dir = Path(os.getenv("RAG_VECTOR_DB_DIR", project_root / "vector_db"))
    manifest_path = vector_db_dir / "ingestion_manifest.json"

    return AppConfig(
        project_root=project_root,
        data_dir=data_dir,
        vector_db_dir=vector_db_dir,
        manifest_path=manifest_path,
        chroma_collection_name=os.getenv("RAG_CHROMA_COLLECTION", "vulnerability_knowledge_base"),
        embedding_model_name=os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "800")),
        chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "120")),
        top_k=int(os.getenv("RAG_TOP_K", "8")),
        llm_model_name=os.getenv("RAG_LLM_MODEL", "gemini-3.5-flash"),
        llm_api_key=os.getenv("GEMINI_API_KEY"),
        llm_temperature=float(os.getenv("RAG_LLM_TEMPERATURE", "0.2")),
    )
