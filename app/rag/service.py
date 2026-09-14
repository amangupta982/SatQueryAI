"""
Unified RAG Service for SatQuery AI.
Coordinates semantic retrieval, evidence thresholding, and grounded answer synthesis.
"""

import logging
from typing import Optional

from app.rag.schemas import RAGQueryRequest, RAGQueryResponse, RAGEvidence, RAGSource
from app.rag.vectorstore import QdrantVectorStore
from app.rag.retriever import KnowledgeRetriever
from app.rag.llm import get_llm_adapter, NO_INFO_MESSAGE

logger = logging.getLogger(__name__)

UNAVAILABLE_MESSAGE = "Knowledge retrieval is currently unavailable."


class RAGService:
    """Singleton service handling end-to-end RAG question answering."""
    _instance = None

    def __init__(self):
        self.vectorstore = QdrantVectorStore.get_instance()
        self.retriever = KnowledgeRetriever(vectorstore=self.vectorstore)
        self.llm_adapter = get_llm_adapter()

    @classmethod
    def get_instance(cls) -> "RAGService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def query(self, req: RAGQueryRequest) -> RAGQueryResponse:
        """
        Executes a grounded domain-knowledge query.
        Guarantees clear error handling if vectorstore is down or no evidence is found.
        """
        query_text = req.query.strip()

        # 1. Check vectorstore availability
        if not self.vectorstore.is_available():
            logger.warning("[RAG Service] Vectorstore is unavailable when querying.")
            return RAGQueryResponse(
                answer=UNAVAILABLE_MESSAGE,
                sources=[],
                evidence=[],
                query=query_text,
                knowledge_available=False
            )

        # 2. Retrieve evidence and sources
        evidence, sources = self.retriever.retrieve(
            query=query_text,
            top_k=req.top_k,
            score_threshold=req.score_threshold
        )

        # 3. Check for empty evidence / below similarity threshold
        if not evidence:
            logger.info(f"[RAG Service] No relevant chunks found for query: '{query_text}'")
            return RAGQueryResponse(
                answer=NO_INFO_MESSAGE,
                sources=[],
                evidence=[],
                query=query_text,
                knowledge_available=True
            )

        # 4. Synthesize grounded answer
        try:
            answer = self.llm_adapter.synthesize_answer(query_text, evidence)
        except Exception as e:
            logger.error(f"[RAG Service] Error during answer synthesis: {e}")
            # Fallback directly to top evidence text if synthesis errors
            answer = evidence[0].text if evidence else NO_INFO_MESSAGE

        return RAGQueryResponse(
            answer=answer,
            sources=sources,
            evidence=evidence,
            query=query_text,
            knowledge_available=True
        )

    def get_status(self) -> dict:
        """Returns health and collection statistics."""
        available = self.vectorstore.is_available()
        count = self.vectorstore.count() if available else 0
        return {
            "status": "ready" if available and count > 0 else ("empty" if available else "unavailable"),
            "vectorstore": "qdrant",
            "collection": self.vectorstore.collection_name,
            "total_chunks_indexed": count,
            "is_available": available
        }
