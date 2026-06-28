from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader

from src.loaders.base import BaseLoader
from src.utils.hashing import hash_file
from src.utils.models import LoadedDocument


class PDFFileLoader(BaseLoader):
    def supports(self, path: Path) -> bool:
        return path.is_file() and path.suffix.lower() == ".pdf"

    def load(self, path: Path) -> LoadedDocument:
        reader = PdfReader(path)
        text_parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        text = "\n\n".join(text_parts).strip()
        category = path.parent.name if path.parent.name.lower() != "data" else None
        return LoadedDocument(
            source_path=path,
            text=text,
            source_filename=path.name,
            document_category=category,
            document_hash=hash_file(path),
        )
