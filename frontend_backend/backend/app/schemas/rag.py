from pydantic import BaseModel, Field
from typing import Optional, List

class DocumentMetadata(BaseModel):
    document_id: str
    title: str
    source: str
    document_type: str
    page_number: Optional[int] = None
    chunk_id: str

class TextChunk(BaseModel):
    text: str
    metadata: DocumentMetadata
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for the chunk")
