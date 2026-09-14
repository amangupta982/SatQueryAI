"""
FastAPI router adapter for RAG Remote Sensing Knowledge.
Exposes router from app.api.routes.rag.
"""

from app.api.routes.rag import router

__all__ = ["router"]
