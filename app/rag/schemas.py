"""
Pydantic schemas for the SatQuery AI RAG Knowledge module.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """Request payload for querying remote sensing knowledge."""
    query: str = Field(..., min_length=2, description="Natural language question about remote sensing domain knowledge")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Maximum number of relevant chunks to retrieve")
    score_threshold: Optional[float] = Field(default=0.25, ge=0.0, le=1.0, description="Minimum cosine similarity threshold")


class RAGSource(BaseModel):
    """Reference document source for retrieved knowledge."""
    document: str = Field(..., description="Document filename or identifier")
    section: Optional[str] = Field(default=None, description="Section heading or topic")
    category: Optional[str] = Field(default="general", description="Folder or subject category (e.g. isro, satellites, remote_sensing)")
    page: Optional[int] = Field(default=None, description="Page number if applicable")


class RAGEvidence(BaseModel):
    """Concrete snippet of evidence retrieved from vector store."""
    text: str = Field(..., description="Excerpt of retrieved text chunk")
    score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    source: str = Field(..., description="Document source name")
    section: Optional[str] = Field(default=None, description="Section header")
    category: Optional[str] = Field(default=None, description="Knowledge category")
    chunk_id: Optional[str] = Field(default=None, description="Unique chunk identifier")


class RAGQueryResponse(BaseModel):
    """Standardized response returned by the RAG query endpoint."""
    answer: str = Field(..., description="Synthesized grounded answer")
    sources: List[RAGSource] = Field(default_factory=list, description="Unique cited sources")
    evidence: List[RAGEvidence] = Field(default_factory=list, description="Top retrieved knowledge snippets")
    query: str = Field(..., description="Original user question")
    knowledge_available: bool = Field(default=True, description="True if vectorstore and knowledge base are available")


class RAGIngestRequest(BaseModel):
    """Parameters for triggering knowledge base ingestion."""
    knowledge_dir: Optional[str] = Field(default=None, description="Custom knowledge directory path if overriding default")
    force_reindex: Optional[bool] = Field(default=False, description="Whether to recreate collection from scratch")


class RAGIngestResponse(BaseModel):
    """Response returned upon completing document ingestion."""
    status: str = Field(..., description="Ingestion status ('success', 'warning', 'error')")
    documents_indexed: int = Field(default=0, description="Number of documents successfully processed")
    total_chunks: int = Field(default=0, description="Total chunks embedded and stored in Qdrant")
    collection_name: str = Field(..., description="Target Qdrant collection name")
    message: str = Field(..., description="Detailed summary message")
