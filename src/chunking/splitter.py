from __future__ import annotations

from dataclasses import dataclass

from src.utils.models import ChunkRecord, LoadedDocument


@dataclass(frozen=True)
class ChunkingConfig:
    chunk_size: int = 800
    chunk_overlap: int = 120


class RecursiveCharacterChunker:
    def __init__(self, config: ChunkingConfig) -> None:
        if config.chunk_overlap >= config.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self._config = config

    def split(self, document: LoadedDocument) -> list[ChunkRecord]:
        text = document.text.strip()
        if not text:
            return []

        chunks: list[ChunkRecord] = []
        start = 0
        chunk_index = 0
        while start < len(text):
            end = min(len(text), start + self._config.chunk_size)
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_id = f"{document.source_filename}::{chunk_index}"
                metadata = {
                    "source_filename": document.source_filename,
                    "chunk_id": chunk_index,
                    "page_number": document.page_number,
                    "document_category": document.document_category,
                    "document_hash": document.document_hash,
                    "source_path": str(document.source_path),
                }
                chunks.append(
                    ChunkRecord(
                        id=chunk_id,
                        text=chunk_text,
                        source_filename=document.source_filename,
                        chunk_id=chunk_index,
                        page_number=document.page_number,
                        document_category=document.document_category,
                        document_hash=document.document_hash or "",
                        source_path=str(document.source_path),
                        metadata=metadata,
                    )
                )
            if end == len(text):
                break
            start = max(end - self._config.chunk_overlap, start + 1)
            chunk_index += 1

        return chunks
