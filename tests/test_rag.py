"""
Isolated test suite for SatQuery AI RAG (Retrieval-Augmented Generation) module.
Tests:
  1. Document chunking & metadata retention
  2. Embedding generation & dimensions
  3. Qdrant vector retrieval
  4. Similarity threshold filtering
  5. RAG query API endpoint (/api/rag/query)
  6. Source metadata provenance
  7. No-result out-of-domain handling
  8. Qdrant unavailable graceful degradation
"""

import os
import sys

# Ensure repository root is on Python path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pytest
from fastapi.testclient import TestClient

from app.rag.chunking import chunk_text, process_document, KnowledgeChunk
from app.rag.embeddings import EmbeddingService
from app.rag.vectorstore import QdrantVectorStore
from app.rag.retriever import KnowledgeRetriever
from app.rag.service import RAGService, UNAVAILABLE_MESSAGE
from app.rag.schemas import RAGQueryRequest
from app.rag.llm import NO_INFO_MESSAGE
from frontend_backend.backend.main import app


@pytest.fixture(scope="module")
def client():
    """FastAPI test client."""
    return TestClient(app)


# ==============================================================================
# 1. DOCUMENT CHUNKING TEST
# ==============================================================================
def test_document_chunking():
    """Verify text chunking preserves paragraph boundaries and respects length constraints."""
    sample_text = (
        "Synthetic Aperture Radar (SAR) is an active microwave system.\n\n"
        "It illuminates the Earth's surface with radar pulses and records backscatter.\n\n"
        "SAR operates day and night through clouds and rain."
    )
    chunks = chunk_text(sample_text, max_chars=120, overlap_chars=20)
    assert len(chunks) >= 2, "Expected multiple chunks for short max_chars"
    for c in chunks:
        assert len(c) <= 150, f"Chunk exceeded reasonable size: {len(c)}"
        assert len(c.strip()) > 0


# ==============================================================================
# 2. EMBEDDING GENERATION TEST
# ==============================================================================
def test_embedding_generation():
    """Verify embeddings produce normalized 384-dimensional vectors."""
    service = EmbeddingService.get_instance()
    query = "What is Synthetic Aperture Radar?"
    vec = service.embed_query(query)
    
    assert isinstance(vec, list)
    assert len(vec) == 384, f"Expected 384 dimensions for all-MiniLM-L6-v2, got {len(vec)}"
    # Vector should be L2-normalized (magnitude ≈ 1.0)
    import math
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 0.05, f"Vector should be unit normalized, norm={norm}"


# ==============================================================================
# 3. QDRANT RETRIEVAL TEST
# ==============================================================================
def test_qdrant_retrieval():
    """Verify Qdrant retrieves relevant chunks for domain queries."""
    retriever = KnowledgeRetriever()
    evidence, sources = retriever.retrieve(query="What is SAR?", top_k=3, score_threshold=0.2)
    
    assert len(evidence) > 0, "Should retrieve at least 1 chunk for core remote sensing query"
    top_chunk = evidence[0]
    assert "sar" in top_chunk.text.lower() or "radar" in top_chunk.text.lower()
    assert top_chunk.score > 0.3


# ==============================================================================
# 4. SIMILARITY THRESHOLD TEST
# ==============================================================================
def test_similarity_threshold_filtering():
    """Verify that chunks below the score threshold are filtered out."""
    retriever = KnowledgeRetriever()
    # High impossible threshold
    evidence_strict, _ = retriever.retrieve(query="What is SAR?", top_k=5, score_threshold=0.99)
    assert len(evidence_strict) == 0, "No chunks should pass a 0.99 cosine threshold"

    # Lenient threshold
    evidence_lenient, _ = retriever.retrieve(query="What is SAR?", top_k=5, score_threshold=0.2)
    assert len(evidence_lenient) > 0, "Chunks should pass lenient 0.2 threshold"


# ==============================================================================
# 5. RAG QUERY API TEST
# ==============================================================================
def test_rag_query_api_endpoint(client):
    """Verify POST /api/rag/query returns correct JSON schema with answer and evidence."""
    payload = {
        "query": "What is the difference between Sentinel-1 and Sentinel-2?",
        "top_k": 3,
        "score_threshold": 0.25
    }
    response = client.post("/api/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "answer" in data
    assert "sources" in data
    assert "evidence" in data
    assert data["knowledge_available"] is True
    assert len(data["sources"]) > 0
    assert len(data["evidence"]) > 0
    assert any("Sentinel" in src["document"] or "sentinel" in src["document"] for src in data["sources"])


# ==============================================================================
# 6. SOURCE METADATA PROVENANCE TEST
# ==============================================================================
def test_source_metadata_provenance():
    """Verify chunks preserve provenance metadata (document, section, category)."""
    retriever = KnowledgeRetriever()
    evidence, sources = retriever.retrieve(query="What is BigEarthNet.txt?", top_k=3)
    
    assert len(sources) > 0
    top_src = sources[0]
    assert top_src.document is not None
    assert top_src.category in ["datasets", "remote_sensing", "project_docs", "isro", "satellites", "research_papers", "general"]
    assert top_src.section is not None


# ==============================================================================
# 7. NO-RESULT HANDLING TEST
# ==============================================================================
def test_no_result_handling():
    """Verify out-of-domain queries return the standardized no-info message without hallucinating."""
    service = RAGService.get_instance()
    # Completely out of domain query with strict threshold
    req = RAGQueryRequest(query="How to bake a chocolate strawberry birthday cake at 350 degrees?", score_threshold=0.5)
    resp = service.query(req)
    
    assert resp.answer == NO_INFO_MESSAGE
    assert len(resp.evidence) == 0
    assert len(resp.sources) == 0


# ==============================================================================
# 8. QDRANT UNAVAILABLE HANDLING TEST
# ==============================================================================
def test_qdrant_unavailable_handling(monkeypatch):
    """Verify system gracefully degrades with clear message if vector store is unavailable."""
    service = RAGService.get_instance()
    
    # Mock vectorstore as unavailable
    monkeypatch.setattr(service.vectorstore, "is_available", lambda: False)
    
    req = RAGQueryRequest(query="What is SAR?")
    resp = service.query(req)
    
    assert resp.answer == UNAVAILABLE_MESSAGE
    assert resp.knowledge_available is False
    assert len(resp.evidence) == 0
    assert len(resp.sources) == 0
