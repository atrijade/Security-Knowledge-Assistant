from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from src.utils.models import LoadedDocument


class BaseLoader(ABC):
    @abstractmethod
    def supports(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def load(self, path: Path) -> LoadedDocument:
        raise NotImplementedError
