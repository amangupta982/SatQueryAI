"""
Ingestion pipeline for the SatQuery AI Remote Sensing Knowledge Base.
Scans knowledge/ subfolders, parses documents, generates embeddings,
and indexes vectors in Qdrant.
"""

import os
import glob
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple

from app.rag.chunking import process_document, KnowledgeChunk
from app.rag.embeddings import EmbeddingService
from app.rag.vectorstore import QdrantVectorStore

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


def get_default_knowledge_dir() -> str:
    """Find the root knowledge/ directory relative to project root."""
    # Check current directory
    candidates = [
        "knowledge",
        os.path.join(os.getcwd(), "knowledge"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "knowledge")),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return "knowledge"


def ingest_knowledge_base(
    knowledge_dir: Optional[str] = None,
    force_reindex: bool = False,
    batch_size: int = 32
) -> Dict[str, Any]:
    """
    Scans the knowledge directory, chunks all documents, computes embeddings,
    and indexes them in the Qdrant vector store.
    """
    root_dir = knowledge_dir or get_default_knowledge_dir()
    if not os.path.exists(root_dir):
        msg = f"Knowledge directory '{root_dir}' not found."
        logger.error(f"[RAG Ingestion] {msg}")
        return {
            "status": "error",
            "documents_indexed": 0,
            "total_chunks": 0,
            "collection_name": "",
            "message": msg
        }

    vectorstore = QdrantVectorStore.get_instance()
    if not vectorstore.is_available():
        msg = "Qdrant vectorstore is currently unavailable for ingestion."
        logger.error(f"[RAG Ingestion] {msg}")
        return {
            "status": "error",
            "documents_indexed": 0,
            "total_chunks": 0,
            "collection_name": vectorstore.collection_name,
            "message": msg
        }

    if force_reindex:
        logger.info(f"[RAG Ingestion] Recreating Qdrant collection '{vectorstore.collection_name}'...")
        vectorstore.recreate_collection()

    embedding_service = EmbeddingService.get_instance()

    # 1. Discover all candidate files
    discovered_files: List[Tuple[str, str]] = []  # (filepath, category)
    for root, _, files in os.walk(root_dir):
        category = os.path.basename(root)
        if category == os.path.basename(root_dir):
            category = "general"
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_EXTENSIONS and not f.startswith("."):
                discovered_files.append((os.path.join(root, f), category))

    if not discovered_files:
        return {
            "status": "warning",
            "documents_indexed": 0,
            "total_chunks": 0,
            "collection_name": vectorstore.collection_name,
            "message": f"No supported documents (.md, .txt, .pdf) found in '{root_dir}'"
        }

    logger.info(f"[RAG Ingestion] Found {len(discovered_files)} documents to ingest.")

    # 2. Extract and chunk all documents
    all_chunks: List[KnowledgeChunk] = []
    docs_processed = 0

    for file_path, category in discovered_files:
        try:
            chunks = process_document(file_path=file_path, category=category)
            if chunks:
                all_chunks.extend(chunks)
                docs_processed += 1
                logger.debug(f"[RAG Ingestion] Processed '{file_path}': {len(chunks)} chunks.")
        except Exception as e:
            logger.error(f"[RAG Ingestion] Failed to process document '{file_path}': {e}")

    if not all_chunks:
        return {
            "status": "warning",
            "documents_indexed": docs_processed,
            "total_chunks": 0,
            "collection_name": vectorstore.collection_name,
            "message": "Documents were parsed but produced 0 valid chunks."
        }

    # 3. Compute embeddings and upsert in batches
    logger.info(f"[RAG Ingestion] Generating embeddings for {len(all_chunks)} chunks...")
    total_upserted = 0

    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        texts = [c.text for c in batch]
        try:
            embeddings = embedding_service.embed_texts(texts)
            points = []
            for chunk, vec in zip(batch, embeddings):
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
                points.append({
                    "id": point_id,
                    "vector": vec,
                    "payload": chunk.to_dict()
                })
            vectorstore.upsert_points(points)
            total_upserted += len(points)
        except Exception as e:
            logger.error(f"[RAG Ingestion] Error indexing batch {i}..{i+batch_size}: {e}")

    summary_msg = f"Successfully ingested {docs_processed} documents into {total_upserted} chunks in Qdrant."
    logger.info(f"[RAG Ingestion] {summary_msg}")

    return {
        "status": "success",
        "documents_indexed": docs_processed,
        "total_chunks": total_upserted,
        "collection_name": vectorstore.collection_name,
        "message": summary_msg
    }
