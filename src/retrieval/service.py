from __future__ import annotations

from dataclasses import dataclass

from src.embeddings.model import SentenceTransformerEmbedder
from src.utils.models import RetrievedChunk
from src.vectordb.chroma_store import ChromaVectorStore


@dataclass(frozen=True)
class RetrievalResponse:
    question: str
    chunks: list[RetrievedChunk]


class RetrievalService:
    def __init__(self, embedder: SentenceTransformerEmbedder, store: ChromaVectorStore) -> None:
        self._embedder = embedder
        self._store = store

    def retrieve(self, question: str, top_k: int) -> RetrievalResponse:
        query_embedding = self._embedder.embed_query(question)
        chunks = self._store.query(query_embedding=query_embedding, top_k=top_k)
        return RetrievalResponse(question=question, chunks=chunks)
