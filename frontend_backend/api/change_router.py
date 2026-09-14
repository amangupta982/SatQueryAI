"""
FastAPI Router for Temporal Change Analysis.

Wraps the grounding_change inference module for multitemporal
change intelligence, interactive follow-up querying, and evidence serving.
"""

import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/change-analysis", tags=["Change Analysis"])

# Upload directory for temporal image pairs
CHANGE_UPLOAD_DIR = Path("outputs/change_uploads")
CHANGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Request models ──

class ChangeAnalysisRequest(BaseModel):
    before_image_id: str
    after_image_id: str
    question: str = "What changed?"
    timestamps: Optional[list] = None
    session_id: Optional[str] = None


class FollowUpQueryRequest(BaseModel):
    session_id: str
    question: str


class RegionFilterRequest(BaseModel):
    session_id: str
    category: Optional[str] = None
    change_type: Optional[str] = None
    confidence_min: Optional[float] = None
    area_min_pixels: Optional[int] = None
    area_min_m2: Optional[float] = None
    top_k: Optional[int] = None


def _get_inference_module():
    """Lazily import grounding_change inference to avoid import errors at startup."""
    try:
        import sys
        project_root = str(Path(__file__).resolve().parents[2])
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from grounding_change.inference import (
            analyze_temporal_scene,
            query_temporal_scene,
            filter_changes,
            export_geojson,
            get_region,
            session_manager,
        )
        from grounding_change.config import OUTPUT_DIR
        return {
            "analyze_temporal_scene": analyze_temporal_scene,
            "query_temporal_scene": query_temporal_scene,
            "filter_changes": filter_changes,
            "export_geojson": export_geojson,
            "get_region": get_region,
            "session_manager": session_manager,
            "OUTPUT_DIR": OUTPUT_DIR,
        }
    except ImportError as e:
        logger.warning(f"grounding_change module not available: {e}")
        return None


@router.post("/upload-and-analyze")
async def upload_and_analyze(
    t1_file: UploadFile = File(..., description="Earlier temporal image (T1)"),
    t2_file: UploadFile = File(..., description="Later temporal image (T2)"),
    question: str = Form(default="What changed?"),
    t1_timestamp: str = Form(default=""),
    t2_timestamp: str = Form(default=""),
):
    """
    Upload two temporal images directly and run comprehensive change analysis.
    """
    mod = _get_inference_module()
    if not mod:
        raise HTTPException(status_code=503, detail="Change analysis module not available.")

    os.makedirs(CHANGE_UPLOAD_DIR, exist_ok=True)

    t1_id = str(uuid.uuid4())
    t1_ext = os.path.splitext(t1_file.filename or "image.png")[1].lower() or ".png"
    t1_path = CHANGE_UPLOAD_DIR / f"{t1_id}{t1_ext}"
    with open(t1_path, "wb") as f:
        shutil.copyfileobj(t1_file.file, f)

    t2_id = str(uuid.uuid4())
    t2_ext = os.path.splitext(t2_file.filename or "image.png")[1].lower() or ".png"
    t2_path = CHANGE_UPLOAD_DIR / f"{t2_id}{t2_ext}"
    with open(t2_path, "wb") as f:
        shutil.copyfileobj(t2_file.file, f)

    session_id = f"session_{uuid.uuid4().hex[:10]}"
    timestamps_tuple = (t1_timestamp, t2_timestamp) if t1_timestamp and t2_timestamp else None

    try:
        from fastapi.concurrency import run_in_threadpool
        output = await run_in_threadpool(
            mod["analyze_temporal_scene"],
            image_t1=str(t1_path),
            image_t2=str(t2_path),
            question=question,
            timestamps=timestamps_tuple,
            metadata=None,
            session_id=session_id,
            return_visuals=True,
            return_geo=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Change analysis failed: {str(e)}")

    evidence_file = ""
    if output.visualizations:
        evidence_file = output.visualizations.complete_overlay or output.visualizations.change_mask or ""

    return {
        "session_id": session_id,
        "t1_image_id": t1_id,
        "t2_image_id": t2_id,
        "answer": output.answer,
        "scene_summary": output.scene_summary.model_dump() if output.scene_summary else None,
        "categories": {k: v.model_dump() for k, v in output.categories.items()} if output.categories else {},
        "regions": [r.model_dump() for r in output.regions] if output.regions else [],
        "transitions": [t.model_dump() for t in output.transitions] if output.transitions else [],
        "geospatial": output.geospatial.model_dump() if output.geospatial else None,
        "statistics": output.statistics,
        "visualizations": output.visualizations.model_dump() if output.visualizations else None,
        "confidence": output.confidence,
        "provenance": output.provenance,
        "evidence_file": evidence_file,
    }


@router.post("/analyze")
async def analyze_change(request: ChangeAnalysisRequest):
    """Analyze change between two pre-uploaded images."""
    mod = _get_inference_module()
    if not mod:
        raise HTTPException(status_code=503, detail="Change analysis module not available.")

    # Find images on disk
    import glob
    matches_t1 = glob.glob(str(CHANGE_UPLOAD_DIR / f"{request.before_image_id}.*"))
    matches_t2 = glob.glob(str(CHANGE_UPLOAD_DIR / f"{request.after_image_id}.*"))

    if not matches_t1:
        raise HTTPException(status_code=404, detail=f"Image {request.before_image_id} not found")
    if not matches_t2:
        raise HTTPException(status_code=404, detail=f"Image {request.after_image_id} not found")

    timestamps_tuple = tuple(request.timestamps) if request.timestamps and len(request.timestamps) >= 2 else None

    try:
        from fastapi.concurrency import run_in_threadpool
        output = await run_in_threadpool(
            mod["analyze_temporal_scene"],
            image_t1=matches_t1[0],
            image_t2=matches_t2[0],
            question=request.question,
            timestamps=timestamps_tuple,
            session_id=request.session_id,
            return_visuals=True,
            return_geo=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Change analysis failed: {str(e)}")

    return {
        "session_id": request.session_id or "unknown",
        "answer": output.answer,
        "scene_summary": output.scene_summary.model_dump() if output.scene_summary else None,
        "categories": {k: v.model_dump() for k, v in output.categories.items()} if output.categories else {},
        "regions": [r.model_dump() for r in output.regions] if output.regions else [],
        "transitions": [t.model_dump() for t in output.transitions] if output.transitions else [],
        "statistics": output.statistics,
        "visualizations": output.visualizations.model_dump() if output.visualizations else None,
    }


@router.post("/query")
async def follow_up_query(request: FollowUpQueryRequest):
    """Follow-up query on an existing temporal analysis session."""
    mod = _get_inference_module()
    if not mod:
        raise HTTPException(status_code=503, detail="Change analysis module not available.")

    from fastapi.concurrency import run_in_threadpool
    res = await run_in_threadpool(mod["query_temporal_scene"], session_id=request.session_id, question=request.question)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.post("/filter")
async def filter_scene_regions(request: RegionFilterRequest):
    """Filter change regions by category, confidence, area, etc."""
    mod = _get_inference_module()
    if not mod:
        raise HTTPException(status_code=503, detail="Change analysis module not available.")

    regions = mod["filter_changes"](
        session_id=request.session_id,
        category=request.category,
        change_type=request.change_type,
        confidence_min=request.confidence_min,
        area_min_pixels=request.area_min_pixels,
        area_min_m2=request.area_min_m2,
        top_k=request.top_k,
    )
    return {"session_id": request.session_id, "regions": regions, "count": len(regions)}


@router.get("/evidence/{filename}")
async def get_evidence_image(filename: str):
    """Serves generated visual evidence files."""
    mod = _get_inference_module()
    evidence_dir = mod["OUTPUT_DIR"] / "evidence" if mod else Path("outputs/evidence")

    target = evidence_dir / filename
    if not target.exists():
        target = CHANGE_UPLOAD_DIR / "evidence" / filename
        if not target.exists():
            raise HTTPException(status_code=404, detail=f"Evidence file {filename} not found")

    return FileResponse(str(target))


@router.get("/session/{session_id}/geojson")
async def get_scene_geojson(session_id: str):
    """Exports detected change regions to GeoJSON."""
    mod = _get_inference_module()
    if not mod:
        raise HTTPException(status_code=503, detail="Change analysis module not available.")

    res = mod["export_geojson"](session_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
