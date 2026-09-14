"""
FastAPI Router for Optical-SAR Multimodal Agent.

Endpoints for co-registered Sentinel-1 SAR + Sentinel-2 Multispectral analysis,
BigEarthNet.txt VQA, Referring Expression Grounding, and Multi-Turn Reasoning.
"""

import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/optical-sar", tags=["Optical-SAR Agent"])

# Upload directory for optical-sar image pairs
OS_UPLOAD_DIR = Path("outputs/optical_sar_uploads")
OS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class OpticalSARFollowUpRequest(BaseModel):
    session_id: str
    question: str


def _get_inference_module():
    """Lazily import grounding_change optical-sar tools."""
    try:
        import sys
        project_root = str(Path(__file__).resolve().parents[2])
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from grounding_change.inference.agent_tools import (
            analyze_optical_sar_scene,
            query_optical_sar_scene,
            get_supported_agent_modes,
        )
        from grounding_change.inference.optical_sar_reasoner import optical_sar_sessions
        from grounding_change.config import settings
        return {
            "analyze_optical_sar_scene": analyze_optical_sar_scene,
            "query_optical_sar_scene": query_optical_sar_scene,
            "get_supported_agent_modes": get_supported_agent_modes,
            "optical_sar_sessions": optical_sar_sessions,
            "settings": settings,
        }
    except Exception as e:
        logger.warning(f"grounding_change optical-sar module not available: {e}", exc_info=True)
        return None


@router.get("/modes")
def list_supported_modes() -> List[Dict[str, str]]:
    """Returns the 7 operational modes of the Optical-SAR Agent."""
    mod = _get_inference_module()
    if mod:
        return mod["get_supported_agent_modes"]()
    return [
        {"id": "optical_only", "label": "Mode 1: Optical Only"},
        {"id": "sar_only", "label": "Mode 2: SAR Only"},
        {"id": "optical_sar", "label": "Mode 3: Optical + SAR Joint Fusion"},
        {"id": "optical_sar_temporal", "label": "Mode 4: Optical + SAR Temporal"},
        {"id": "optical_sar_vqa", "label": "Mode 5: BigEarthNet.txt VQA"},
        {"id": "optical_sar_vqa_grounding", "label": "Mode 6: VQA + Visual Grounding"},
        {"id": "optical_sar_full_geospatial", "label": "Mode 7: Full Geospatial Agent"},
    ]


@router.post("/analyze")
async def analyze_optical_sar(
    optical_file: UploadFile = File(...),
    sar_file: Optional[UploadFile] = File(None),
    question: Optional[str] = Form(None),
    referring_expression: Optional[str] = Form(None),
    agent_mode: Optional[str] = Form("optical_sar_full_geospatial"),
    optical_timestamp: Optional[str] = Form(None),
    sar_timestamp: Optional[str] = Form(None),
) -> Dict[str, Any]:
    """
    Accepts multipart uploads of Optical (Sentinel-2) and SAR (Sentinel-1) files,
    runs full foundation perception, cross-modal fusion, and returns structured result.
    """
    mod = _get_inference_module()
    if not mod:
        raise HTTPException(status_code=503, detail="Optical-SAR analysis module not available.")

    session_prefix = uuid.uuid4().hex[:8]

    opt_ext = Path(optical_file.filename or "opt.png").suffix or ".png"
    opt_path = OS_UPLOAD_DIR / f"upload_{session_prefix}_optical{opt_ext}"
    with open(opt_path, "wb") as buffer:
        shutil.copyfileobj(optical_file.file, buffer)

    sar_path = None
    if sar_file is not None and sar_file.filename:
        sar_ext = Path(sar_file.filename).suffix or ".png"
        sar_path = OS_UPLOAD_DIR / f"upload_{session_prefix}_sar{sar_ext}"
        with open(sar_path, "wb") as buffer:
            shutil.copyfileobj(sar_file.file, buffer)

    try:
        from fastapi.concurrency import run_in_threadpool
        result = await run_in_threadpool(
            mod["analyze_optical_sar_scene"],
            optical_image=opt_path,
            sar_image=sar_path,
            question=question,
            referring_expression=referring_expression,
            optical_timestamp=optical_timestamp,
            sar_timestamp=sar_timestamp,
            agent_mode=agent_mode or "optical_sar_full_geospatial",
        )

        return {
            "session_id": result.scene.scene_id,
            "answer": result.answer,
            "mode_applied": result.mode_applied,
            "is_temporal_change": result.is_temporal_change,
            "categories_detected": result.scene.categories_detected,
            "category_proportions": result.scene.category_proportions,
            "cross_modal_difference": result.scene.cross_modal_difference.model_dump(),
            "evidence_urls": result.evidence_urls,
            "grounded_boxes": result.grounded_boxes,
            "sensor_metadata": result.scene.sensor_metadata.model_dump(),
            "confidence": result.confidence,
        }
    except Exception as e:
        logger.error(f"Error analyzing Optical-SAR scene: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
def query_optical_sar(request: OpticalSARFollowUpRequest) -> Dict[str, Any]:
    """Interactive follow-up question on an existing Optical-SAR scene."""
    mod = _get_inference_module()
    if not mod:
        raise HTTPException(status_code=503, detail="Optical-SAR analysis module not available.")

    res = mod["query_optical_sar_scene"](request.session_id, request.question)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.get("/session/{session_id}")
def get_session_scene(session_id: str) -> Dict[str, Any]:
    """Returns the full cached scene representation."""
    mod = _get_inference_module()
    if not mod:
        raise HTTPException(status_code=503, detail="Optical-SAR analysis module not available.")

    scene = mod["optical_sar_sessions"].get_scene(session_id)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    return scene.model_dump()


@router.get("/evidence/{filename}")
def get_evidence_image(filename: str):
    """Serves generated visual evidence images."""
    evidence_dir = Path("outputs/optical_sar_evidence")
    path = evidence_dir / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Evidence file not found")
    return FileResponse(str(path))
