import pytest
import os
import shutil
import uuid
from app.services.rag.chunker import TextChunker
from app.services.rag.embedder import EmbeddingService
from app.services.rag.qdrant import QdrantService
from app.schemas.rag import TextChunk, DocumentMetadata
from app.core.config import core_settings

@pytest.fixture(scope="module")
def qdrant_service():
    # Use a temporary directory for testing Qdrant
    test_qdrant_path = os.path.join(core_settings.BASE_DIR, "data", "test_qdrant")
    
    # Temporarily override the config
    original_path = core_settings.QDRANT_PATH
    core_settings.QDRANT_PATH = test_qdrant_path
    
    if os.path.exists(test_qdrant_path):
        shutil.rmtree(test_qdrant_path)
        
    service = QdrantService(collection_name="test_knowledge")
    
    yield service
    
    # Cleanup
    if os.path.exists(test_qdrant_path):
        shutil.rmtree(test_qdrant_path)
    core_settings.QDRANT_PATH = original_path


def test_chunker():
    raw_docs = [
        {
            "text": "A" * 1000 + "B" * 500, # 1500 chars total
            "title": "Test Doc",
            "source": "/fake/path.txt",
            "document_type": "isro",
            "page_number": None
        }
    ]
    
    chunker = TextChunker(chunk_size=1000, overlap=200)
    chunks = chunker.chunk_documents(raw_docs)
    
    assert len(chunks) == 2
    assert len(chunks[0].text) == 1000
    # Next chunk should start 200 chars back from the end of the first chunk
    # So it contains the last 200 As and 500 Bs = 700 length
    assert len(chunks[1].text) == 700
    
    # Check metadata
    assert chunks[0].metadata.title == "Test Doc"
    assert chunks[0].metadata.document_type == "isro"
    assert chunks[0].metadata.document_id == chunks[1].metadata.document_id
    assert chunks[0].metadata.chunk_id != chunks[1].metadata.chunk_id


def test_embedder():
    chunks = [
        TextChunk(
            text="Satellite imagery analysis.",
            metadata=DocumentMetadata(
                document_id="doc1", title="A", source="A", document_type="A", chunk_id="chunk1"
            ),
            embedding=None
        )
    ]
    
    embedder = EmbeddingService()
    embedded = embedder.embed_chunks(chunks)
    
    assert len(embedded) == 1
    assert embedded[0].embedding is not None
    assert len(embedded[0].embedding) == 384 # all-MiniLM-L6-v2 dimension


def test_qdrant_ingestion(qdrant_service):
    # Create mock embedded chunks
    doc_id = "test_doc_id"
    chunks = [
        TextChunk(
            text="First part of document.",
            metadata=DocumentMetadata(
                document_id=doc_id, title="Test", source="Test", document_type="isro", chunk_id=str(uuid.uuid4())
            ),
            embedding=[0.1] * 384
        ),
        TextChunk(
            text="Second part of document.",
            metadata=DocumentMetadata(
                document_id=doc_id, title="Test", source="Test", document_type="isro", chunk_id=str(uuid.uuid4())
            ),
            embedding=[0.2] * 384
        )
    ]
    
    # 1. Initial ingestion
    inserted = qdrant_service.ingest_chunks(chunks)
    assert inserted == 2
    
    # 2. Duplicate ingestion should be prevented
    inserted_again = qdrant_service.ingest_chunks(chunks)
    assert inserted_again == 0
    
    # 3. New document ingestion
    new_doc_id = "test_doc_id_2"
    new_chunks = [
        TextChunk(
            text="A completely new document.",
            metadata=DocumentMetadata(
                document_id=new_doc_id, title="Test2", source="Test2", document_type="isro", chunk_id=str(uuid.uuid4())
            ),
            embedding=[0.3] * 384
        )
    ]
    inserted_new = qdrant_service.ingest_chunks(new_chunks)
    assert inserted_new == 1
