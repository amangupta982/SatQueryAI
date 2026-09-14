import hashlib
import uuid
from typing import List, Dict, Any
from app.schemas.rag import TextChunk, DocumentMetadata

class TextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_documents(self, raw_docs: List[Dict[str, Any]]) -> List[TextChunk]:
        """
        Takes raw document dicts (with 'text', 'title', 'source', 'document_type', 'page_number')
        and breaks them into chunks based on char size and overlap.
        """
        chunks = []
        for doc in raw_docs:
            text = doc["text"]
            if not text:
                continue
                
            # Create a base document_id based on the source path
            document_id = hashlib.md5(doc["source"].encode("utf-8")).hexdigest()
            
            # Simple character-based sliding window
            start = 0
            text_len = len(text)
            
            while start < text_len:
                end = min(start + self.chunk_size, text_len)
                chunk_text = text[start:end]
                
                # If we're not at the very end, try to snap to the nearest whitespace to avoid cutting words
                if end < text_len:
                    last_space = chunk_text.rfind(' ')
                    if last_space != -1 and last_space > self.chunk_size // 2:
                        end = start + last_space
                        chunk_text = text[start:end]
                
                chunk_id = str(uuid.uuid4())
                
                metadata = DocumentMetadata(
                    document_id=document_id,
                    title=doc.get("title", "Unknown"),
                    source=doc.get("source", "Unknown"),
                    document_type=doc.get("document_type", "Unknown"),
                    page_number=doc.get("page_number"),
                    chunk_id=chunk_id
                )
                
                chunks.append(TextChunk(
                    text=chunk_text.strip(),
                    metadata=metadata,
                    embedding=None
                ))
                
                start = end - self.overlap
                # Prevent infinite loops if overlap >= chunk_size
                if start <= end - self.chunk_size + self.overlap:
                    start = end
                    
        return chunks
