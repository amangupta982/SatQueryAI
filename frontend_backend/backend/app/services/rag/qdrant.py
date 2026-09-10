import os
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.schemas.rag import TextChunk
from app.core.config import core_settings

class QdrantService:
    def __init__(self, collection_name: str = "satquery_knowledge"):
        self.collection_name = collection_name
        # Use local disk storage
        os.makedirs(core_settings.QDRANT_PATH, exist_ok=True)
        self.client = QdrantClient(path=core_settings.QDRANT_PATH)
        self._ensure_collection()

    def _ensure_collection(self):
        """Creates the collection if it does not exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            # sentence-transformers 'all-MiniLM-L6-v2' outputs 384 dimensions
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384, 
                    distance=models.Distance.COSINE
                ),
            )

    def ingest_chunks(self, chunks: List[TextChunk]) -> int:
        """
        Inserts chunks into Qdrant. Returns number of newly inserted chunks.
        Prevents duplicate document insertion by checking document_id.
        """
        if not chunks:
            return 0
            
        # 1. Find unique document_ids in this batch
        incoming_doc_ids = list(set(chunk.metadata.document_id for chunk in chunks))
        
        # 2. Check which ones already exist
        # We can do this by querying Qdrant with a filter on document_id
        existing_doc_ids = set()
        for doc_id in incoming_doc_ids:
            res = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=doc_id),
                        )
                    ]
                ),
                limit=1,
                with_payload=False,
                with_vectors=False
            )
            # res is a tuple: (points, next_page_offset)
            if res[0]:
                existing_doc_ids.add(doc_id)
                
        # 3. Filter out chunks that belong to existing documents
        new_chunks = [c for c in chunks if c.metadata.document_id not in existing_doc_ids]
        
        if not new_chunks:
            return 0
            
        # 4. Insert new chunks
        points = []
        for chunk in new_chunks:
            payload = chunk.metadata.model_dump()
            payload["text"] = chunk.text
            
            points.append(
                models.PointStruct(
                    id=chunk.metadata.chunk_id,  # UUID string is a valid point ID
                    vector=chunk.embedding,
                    payload=payload
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return len(new_chunks)
