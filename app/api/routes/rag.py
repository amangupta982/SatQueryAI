"""
FastAPI Router for RAG (Retrieval-Augmented Generation) Remote Sensing Knowledge.
Exposes endpoints:
  - POST /api/rag/query
  - POST /api/rag/ingest
  - GET /api/rag/status
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, status

from app.rag.schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGIngestRequest,
    RAGIngestResponse,
)
from app.rag.service import RAGService
from app.rag.ingestion import ingest_knowledge_base

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG / Remote Sensing Knowledge"])


@router.post("/query", response_model=RAGQueryResponse, summary="Query Remote Sensing Knowledge")
def query_knowledge(req: RAGQueryRequest):
    """
    Query the remote sensing domain knowledge base.
    Returns a grounded natural-language answer, cited sources, and retrieved evidence snippets.
    """
    try:
        service = RAGService.get_instance()
        return service.query(req)
    except Exception as e:
        logger.error(f"[RAG API] Error answering query '{req.query}': {e}", exc_info=True)
        # Avoid crashing the application; return clean fallback
        return RAGQueryResponse(
            answer="Knowledge retrieval encountered an unexpected internal error.",
            sources=[],
            evidence=[],
            query=req.query,
            knowledge_available=False
        )


@router.post("/ingest", response_model=RAGIngestResponse, summary="Ingest Knowledge Documents")
def ingest_documents(req: RAGIngestRequest = RAGIngestRequest()):
    """
    Trigger ingestion of knowledge documents into the Qdrant vector database.
    Processes .md, .txt, and .pdf documents from the knowledge/ directory.
    """
    try:
        result = ingest_knowledge_base(
            knowledge_dir=req.knowledge_dir,
            force_reindex=req.force_reindex
        )
        return RAGIngestResponse(**result)
    except Exception as e:
        logger.error(f"[RAG API] Ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Knowledge base ingestion failed: {str(e)}"
        )


@router.get("/status", summary="Check RAG System Status")
def rag_status():
    """
    Check availability of Qdrant vectorstore and collection statistics.
    """
    service = RAGService.get_instance()
    return service.get_status()
