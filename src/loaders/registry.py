from __future__ import annotations

from pathlib import Path

from src.loaders.base import BaseLoader
from src.loaders.txt_loader import TextFileLoader
from src.loaders.pdf_loader import PDFFileLoader
from src.utils.models import LoadedDocument


class LoaderRegistry:
    def __init__(self, loaders: list[BaseLoader] | None = None) -> None:
        self._loaders = loaders or [TextFileLoader(), PDFFileLoader()]

    def load(self, path: Path) -> LoadedDocument:
        for loader in self._loaders:
            if loader.supports(path):
                return loader.load(path)
        raise ValueError(f"No loader registered for file: {path}")
