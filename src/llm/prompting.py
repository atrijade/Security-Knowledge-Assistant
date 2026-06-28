from __future__ import annotations

from src.retrieval.service import RetrievalResponse


def build_context_block(retrieval: RetrievalResponse) -> str:
    lines: list[str] = []
    for index, chunk in enumerate(retrieval.chunks, start=1):
        source = chunk.metadata.get("source_filename", "unknown")
        chunk_id = chunk.metadata.get("chunk_id", "unknown")
        distance = chunk.distance if chunk.distance is not None else "n/a"
        lines.append(f"[{index}] source={source} chunk={chunk_id} distance={distance}\n{chunk.text}")
    return "\n\n".join(lines)
