from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model = self._load_model(model_name)

    @staticmethod
    @lru_cache(maxsize=4)
    def _load_model(model_name: str) -> SentenceTransformer:
        return SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        vector = self._model.encode([text], normalize_embeddings=True)[0]
        return vector.tolist()
