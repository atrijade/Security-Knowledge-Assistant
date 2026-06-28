from __future__ import annotations

import argparse
import logging
from pathlib import Path

from config import get_config
from src.chunking.splitter import ChunkingConfig, RecursiveCharacterChunker
from src.embeddings.model import SentenceTransformerEmbedder
from src.loaders.registry import LoaderRegistry
from src.utils.logging import configure_logging
from src.utils.manifest import load_manifest, save_manifest
from src.vectordb.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)


def discover_text_files(data_dir: Path) -> list[Path]:
    extensions = {".txt", ".pdf"}
    return sorted(path for path in data_dir.rglob("*") if path.is_file() and path.suffix.lower() in extensions)


def run_ingestion() -> None:
    config = get_config()
    configure_logging()

    if not config.data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {config.data_dir}")

    loader_registry = LoaderRegistry()
    chunker = RecursiveCharacterChunker(
        ChunkingConfig(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    )
    embedder = SentenceTransformerEmbedder(config.embedding_model_name)
    vector_store = ChromaVectorStore(config.vector_db_dir, config.chroma_collection_name)

    current_manifest: dict[str, str] = {}
    previous_manifest = load_manifest(config.manifest_path)

    all_files = discover_text_files(config.data_dir)
    seen_filenames: set[str] = set()

    for file_path in all_files:
        document = loader_registry.load(file_path)
        seen_filenames.add(document.source_filename)
        current_manifest[document.source_filename] = document.document_hash or ""

        if previous_manifest.get(document.source_filename) == document.document_hash:
            logger.info("Skipping unchanged file: %s", document.source_filename)
            continue

        logger.info("Indexing file: %s", document.source_filename)
        vector_store.delete_by_source_filename(document.source_filename)
        chunks = chunker.split(document)
        if not chunks:
            logger.warning("No chunks generated for file: %s", document.source_filename)
            continue

        embeddings = embedder.embed_documents([chunk.text for chunk in chunks])
        vector_store.upsert_chunks(chunks, embeddings)
        logger.info("Indexed %d chunks from %s", len(chunks), document.source_filename)

    removed_files = set(previous_manifest) - seen_filenames
    for removed in sorted(removed_files):
        logger.info("Removing deleted file from vector store: %s", removed)
        vector_store.delete_by_source_filename(removed)

    save_manifest(config.manifest_path, current_manifest)
    logger.info("Ingestion complete")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest local security documents into ChromaDB")
    parser.parse_args()
    run_ingestion()


if __name__ == "__main__":
    main()
