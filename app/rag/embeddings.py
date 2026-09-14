"""
Embedding generation service using Sentence Transformers.
Defaults to 'all-MiniLM-L6-v2' (384-dimensional dense embeddings).
"""

import os
import logging
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class EmbeddingService:
    """Manages sentence embedding generation with lazy model initialization."""
    _instance = None

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    @classmethod
    def get_instance(cls, model_name: str = DEFAULT_MODEL_NAME) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls(model_name=model_name)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                import torch

                # Device selection
                if torch.backends.mps.is_available():
                    device = "mps"
                elif torch.cuda.is_available():
                    device = "cuda"
                else:
                    device = "cpu"

                logger.info(f"[RAG] Loading SentenceTransformer model '{self.model_name}' on device: {device}")
                self._model = SentenceTransformer(self.model_name, device=device)
            except Exception as e:
                logger.error(f"[RAG] Error loading SentenceTransformer '{self.model_name}': {e}")
                raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Compute normalized vector embeddings for a list of text strings."""
        if not texts:
            return []
        self._load_model()
        embeddings = self._model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Compute normalized vector embedding for a single user query."""
        self._load_model()
        vec = self._model.encode(
            query,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return vec.tolist()

    @property
    def embedding_dimension(self) -> int:
        """Vector dimensionality (384 for all-MiniLM-L6-v2)."""
        self._load_model()
        return self._model.get_sentence_embedding_dimension()
