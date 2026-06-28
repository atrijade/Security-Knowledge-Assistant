from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LoadedDocument:
    source_path: Path
    text: str
    source_filename: str
    document_category: str | None = None
    page_number: int | None = None
    document_hash: str | None = None


@dataclass(frozen=True)
class ChunkRecord:
    id: str
    text: str
    source_filename: str
    chunk_id: int
    page_number: int | None
    document_category: str | None
    document_hash: str
    source_path: str
    metadata: dict[str, str | int | None] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    text: str
    distance: float | None
    metadata: dict[str, str | int | None]
