"""
Retriever component: generates query embedding, searches vector store,
applies thresholds, and packages knowledge provenance.
"""

import os
import logging
from typing import List, Tuple, Dict, Any, Optional

from app.rag.schemas import RAGEvidence, RAGSource
from app.rag.embeddings import EmbeddingService
from app.rag.vectorstore import QdrantVectorStore

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
DEFAULT_SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", "0.25"))


class KnowledgeRetriever:
    """Orchestrates query vectorization and semantic search against Qdrant."""

    def __init__(
        self,
        vectorstore: Optional[QdrantVectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        top_k: int = DEFAULT_TOP_K,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD
    ):
        self.vectorstore = vectorstore or QdrantVectorStore.get_instance()
        self.embedding_service = embedding_service or EmbeddingService.get_instance()
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> Tuple[List[RAGEvidence], List[RAGSource]]:
        """
        Retrieves top relevant evidence snippets and deduplicated source references.
        """
        k = top_k if top_k is not None else self.top_k
        threshold = score_threshold if score_threshold is not None else self.score_threshold

        if not self.vectorstore.is_available():
            logger.warning("[RAG Retriever] Vectorstore is unavailable. Returning empty results.")
            return [], []

        # 1. Generate query embedding
        try:
            query_vector = self.embedding_service.embed_query(query)
        except Exception as e:
            logger.error(f"[RAG Retriever] Failed to generate embedding for query: {e}")
            return [], []

        # 2. Search Qdrant
        raw_hits = self.vectorstore.search(
            query_vector=query_vector,
            top_k=k,
            score_threshold=threshold
        )

        evidence_list: List[RAGEvidence] = []
        sources_dict: Dict[str, RAGSource] = {}

        for hit in raw_hits:
            payload = hit.get("payload", {})
            text = payload.get("text", "")
            score = round(float(hit.get("score", 0.0)), 3)
            doc_name = payload.get("document", "Unknown Document")
            sec_name = payload.get("section", "General")
            category = payload.get("category", "general")
            page = payload.get("page")
            chunk_id = payload.get("chunk_id", str(hit.get("id")))

            evidence = RAGEvidence(
                text=text,
                score=score,
                source=f"{category}/{doc_name}",
                section=sec_name,
                category=category,
                chunk_id=chunk_id
            )
            evidence_list.append(evidence)

            # Deduplicate sources
            src_key = f"{category}/{doc_name}:{sec_name}"
            if src_key not in sources_dict:
                sources_dict[src_key] = RAGSource(
                    document=doc_name,
                    section=sec_name,
                    category=category,
                    page=page
                )

        return evidence_list, list(sources_dict.values())
