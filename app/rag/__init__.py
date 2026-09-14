"""
SatQuery AI RAG (Retrieval-Augmented Generation) Knowledge Module.
Provides isolated, grounded domain-knowledge query and ingestion pipelines.
"""

from app.rag.schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSource,
    RAGEvidence,
    RAGIngestRequest,
    RAGIngestResponse,
)
from app.rag.service import RAGService
from app.rag.ingestion import ingest_knowledge_base

__all__ = [
    "RAGQueryRequest",
    "RAGQueryResponse",
    "RAGSource",
    "RAGEvidence",
    "RAGIngestRequest",
    "RAGIngestResponse",
    "RAGService",
    "ingest_knowledge_base",
]
