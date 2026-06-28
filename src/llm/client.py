from __future__ import annotations

from dataclasses import dataclass
import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class LLMConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMRequest:
    question: str
    context: str


class GeminiLLMClient:
    def __init__(self, api_key: str | None, model_name: str, temperature: float = 0.2) -> None:
        if not api_key:
            raise LLMConfigurationError(
                "GEMINI_API_KEY is not configured. Set it in your .env file before running query.py."
            )
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name
        self._temperature = temperature

    def answer(self, request: LLMRequest) -> str:
        prompt = (
            "You are a cybersecurity assistant specializing in vulnerability management. "
            "Answer using only the provided context when possible. If context is insufficient, say so clearly.\n\n"
            f"Question: {request.question}\n\n"
            f"Context:\n{request.context}\n\n"
            "Answer:"
        )

        response = self._client.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self._temperature,
            ),
        )
        return response.text or ""
