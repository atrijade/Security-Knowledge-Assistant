from __future__ import annotations

import argparse
import logging

from config import get_config
from src.embeddings.model import SentenceTransformerEmbedder
from src.llm.client import LLMConfigurationError, LLMRequest, GeminiLLMClient
from src.llm.prompting import build_context_block
from src.retrieval.service import RetrievalService
from src.utils.logging import configure_logging
from src.vectordb.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)


def run_query(question: str) -> str:
    config = get_config()
    configure_logging()

    embedder = SentenceTransformerEmbedder(config.embedding_model_name)
    store = ChromaVectorStore(config.vector_db_dir, config.chroma_collection_name)
    retrieval_service = RetrievalService(embedder, store)
    retrieval = retrieval_service.retrieve(question, config.top_k)
    context = build_context_block(retrieval)

    print("\nRetrieved context:\n")
    print(context if context else "No context retrieved.")

    llm_client = GeminiLLMClient(
        api_key=config.llm_api_key,
        model_name=config.llm_model_name,
        temperature=config.llm_temperature,
    )
    answer = llm_client.answer(LLMRequest(question=question, context=context))
    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the vulnerability management RAG assistant")
    parser.add_argument("--question", type=str, help="User question to answer")
    args = parser.parse_args()

    question = args.question or input("Enter your question: ").strip()
    if not question:
        raise ValueError("Question cannot be empty")

    try:
        answer = run_query(question)
    except LLMConfigurationError as exc:
        raise SystemExit(str(exc)) from exc

    print("\nAnswer:\n")
    print(answer)


if __name__ == "__main__":
    main()
