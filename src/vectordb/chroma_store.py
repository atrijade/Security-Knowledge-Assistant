from __future__ import annotations

from pathlib import Path

import chromadb

from src.utils.models import ChunkRecord, RetrievedChunk


class ChromaVectorStore:
    def __init__(self, persist_dir: Path, collection_name: str) -> None:
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[ChunkRecord], embeddings: list[list[float]]) -> None:
        if not chunks:
            return

        self._collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[self._normalize_metadata(chunk.metadata) for chunk in chunks],
        )

    def delete_by_source_filename(self, source_filename: str) -> None:
        self._collection.delete(where={"source_filename": source_filename})

    def query(self, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        retrieved: list[RetrievedChunk] = []
        for index, chunk_id in enumerate(ids):
            retrieved.append(
                RetrievedChunk(
                    id=chunk_id,
                    text=documents[index],
                    distance=distances[index] if index < len(distances) else None,
                    metadata=metadatas[index] if index < len(metadatas) else {},
                )
            )
        return retrieved

    @staticmethod
    def _normalize_metadata(metadata: dict[str, object]) -> dict[str, object]:
        normalized: dict[str, object] = {}
        for key, value in metadata.items():
            if value is None:
                normalized[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                normalized[key] = value
            else:
                normalized[key] = str(value)
        return normalized
