from typing import List
from sentence_transformers import SentenceTransformer
from app.schemas.rag import TextChunk

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the sentence transformer model.
        """
        self.model = SentenceTransformer(model_name)

    def embed_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """
        Generates embeddings for a list of chunks and attaches them to the chunk objects.
        """
        if not chunks:
            return []
            
        texts = [chunk.text for chunk in chunks]
        # Generate embeddings as a list of lists of floats
        embeddings = self.model.encode(texts, convert_to_numpy=True).tolist()
        
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]
            
        return chunks
