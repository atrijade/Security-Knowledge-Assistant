from __future__ import annotations

from pathlib import Path

from src.loaders.base import BaseLoader
from src.utils.hashing import hash_file
from src.utils.models import LoadedDocument


class TextFileLoader(BaseLoader):
    def supports(self, path: Path) -> bool:
        return path.is_file() and path.suffix.lower() == ".txt"

    def load(self, path: Path) -> LoadedDocument:
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        category = path.parent.name if path.parent.name.lower() != "data" else None
        return LoadedDocument(
            source_path=path,
            text=text,
            source_filename=path.name,
            document_category=category,
            document_hash=hash_file(path),
        )

