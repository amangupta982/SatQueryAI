"""
FastAPI application for SatQuery AI.
Integrates SatQuery-VQA inference, geospatial analysis, area measurement,
change analysis, and optical-SAR multimodal agent services.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from frontend_backend.api.vqa_router import router as vqa_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SatQuery AI Backend",
    description="Agentic multimodal AI system for remote-sensing & satellite image analysis.",
    version="1.0.0",
)

# Enable CORS for React frontend (default vite dev server is http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(vqa_router)

# Register Area Measurement + Object Grounding router
try:
    from frontend_backend.api.area_router import router as area_router
    app.include_router(area_router)
    logger.info("[Backend] Area Measurement & Grounding router registered.")
except Exception as e:
    logger.warning(f"[Backend] Area Measurement router not available: {e}")

# Register Change Analysis router
try:
    from frontend_backend.api.change_router import router as change_router
    app.include_router(change_router)
    logger.info("[Backend] Change Analysis router registered.")
except Exception as e:
    logger.warning(f"[Backend] Change Analysis router not available: {e}")

# Register Optical-SAR Multimodal Agent router
try:
    from frontend_backend.api.optical_sar_router import router as optical_sar_router
    app.include_router(optical_sar_router)
    logger.info("[Backend] Optical-SAR Agent router registered.")
except Exception as e:
    logger.warning(f"[Backend] Optical-SAR Agent router not available: {e}")

# Register RAG / Remote Sensing Knowledge router
try:
    from frontend_backend.api.rag_router import router as rag_router
    app.include_router(rag_router)
    logger.info("[Backend] RAG Remote Sensing Knowledge router registered.")
except Exception as e:
    logger.warning(f"[Backend] RAG router not available: {e}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "SatQuery AI Backend", "vqa_model": "SatQuery-VQA"}

@app.get("/")
def root():
    return {"message": "SatQuery AI API Server is running. Visit /docs for OpenAPI documentation."}
