"""
Qdrant Vector Store integration for SatQuery AI.
Supports both remote Qdrant server (QDRANT_URL) and embedded local disk storage.
"""

import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION = os.getenv("QDRANT_COLLECTION", "remote_sensing_knowledge")
DEFAULT_VECTOR_DIM = 384  # Matches all-MiniLM-L6-v2


class QdrantVectorStore:
    """Manages Qdrant client lifecycle, collection creation, and similarity search."""
    _instance = None

    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION,
        vector_dim: int = DEFAULT_VECTOR_DIM,
        url: Optional[str] = None,
        storage_path: Optional[str] = None
    ):
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.url = url or os.getenv("QDRANT_URL")
        self.storage_path = storage_path or os.getenv("QDRANT_STORAGE_PATH", "data/qdrant_storage")
        self.client = None
        self._is_available = False
        self._initialize_client()

    @classmethod
    def get_instance(cls) -> "QdrantVectorStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_client(self):
        """Attempts connection to remote Qdrant, falling back to local embedded storage."""
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        # Try remote URL if provided
        if self.url:
            try:
                logger.info(f"[RAG Qdrant] Attempting remote connection to {self.url}...")
                client = QdrantClient(url=self.url, timeout=3.0)
                # Test connectivity
                client.get_collections()
                self.client = client
                self._is_available = True
                logger.info(f"[RAG Qdrant] Successfully connected to remote Qdrant at {self.url}")
                self._ensure_collection()
                return
            except Exception as e:
                logger.warning(f"[RAG Qdrant] Remote Qdrant at {self.url} unavailable ({e}). Falling back to local disk storage.")

        # Fallback to local embedded storage
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            logger.info(f"[RAG Qdrant] Initializing embedded Qdrant at local path: {self.storage_path}")
            self.client = QdrantClient(path=self.storage_path)
            self._is_available = True
            logger.info(f"[RAG Qdrant] Embedded Qdrant initialized successfully.")
            self._ensure_collection()
        except Exception as e:
            logger.error(f"[RAG Qdrant] Failed to initialize Qdrant client: {e}")
            self._is_available = False
            self.client = None

    def is_available(self) -> bool:
        """Check if vectorstore is active and operational."""
        return self._is_available and self.client is not None

    def _ensure_collection(self):
        """Ensure the target collection exists with Cosine distance metric."""
        if not self.is_available():
            return
        try:
            from qdrant_client.models import Distance, VectorParams
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                logger.info(f"[RAG Qdrant] Creating collection '{self.collection_name}' (dim={self.vector_dim}, Distance=Cosine)...")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
                )
                logger.info(f"[RAG Qdrant] Collection '{self.collection_name}' ready.")
            else:
                logger.debug(f"[RAG Qdrant] Collection '{self.collection_name}' already exists.")
        except Exception as e:
            logger.error(f"[RAG Qdrant] Error creating/checking collection '{self.collection_name}': {e}")
            self._is_available = False

    def recreate_collection(self):
        """Force recreate the collection (for re-indexing)."""
        if not self.is_available():
            self._initialize_client()
        if not self.is_available():
            raise RuntimeError("Qdrant is not available to recreate collection.")

        from qdrant_client.models import Distance, VectorParams
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
        )

    def upsert_points(self, points: List[Dict[str, Any]]):
        """
        Upsert a batch of points into Qdrant.
        points is a list of dicts: [{"id": int/str, "vector": List[float], "payload": Dict[str, Any]}]
        """
        if not self.is_available():
            raise RuntimeError("Qdrant vectorstore is currently unavailable.")

        from qdrant_client.models import PointStruct
        qdrant_points = [
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"]
            )
            for p in points
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=qdrant_points
        )

    def search(self, query_vector: List[float], top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Perform vector cosine similarity search.
        Returns list of dicts: [{"id": ..., "score": float, "payload": dict}]
        """
        if not self.is_available():
            logger.warning("[RAG Qdrant] Search attempted while Qdrant is unavailable.")
            return []

        try:
            # Query Qdrant
            # Supports both query_points (newer qdrant-client) and search
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold if score_threshold > 0 else None,
                    with_payload=True
                )
                results = []
                for pt in response.points:
                    results.append({
                        "id": pt.id,
                        "score": float(pt.score),
                        "payload": pt.payload or {}
                    })
                return results
            else:
                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold if score_threshold > 0 else None,
                    with_payload=True
                )
                return [
                    {
                        "id": hit.id,
                        "score": float(hit.score),
                        "payload": hit.payload or {}
                    }
                    for hit in hits
                ]
        except Exception as e:
            logger.error(f"[RAG Qdrant] Error during vector search: {e}")
            return []

    def count(self) -> int:
        """Count total vectors indexed in collection."""
        if not self.is_available():
            return 0
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception:
            return 0
