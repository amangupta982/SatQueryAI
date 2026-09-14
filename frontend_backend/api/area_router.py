"""
FastAPI Router for Area Measurement and Object Grounding.

Endpoints:
  POST /api/v1/area/analyze   — land-cover area measurement
  POST /api/v1/area/ground    — open-vocabulary object grounding
  GET  /api/v1/area/download  — download latest annotated image
"""

import io
import base64
import logging
from typing import Optional

import numpy as np
from PIL import Image
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/area", tags=["Area Measurement & Grounding"])

# Store latest result for download
_latest_result = {}

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _numpy_to_base64(img_array: np.ndarray, fmt: str = "PNG") -> str:
    """Convert numpy RGB array to base64-encoded string."""
    img = Image.fromarray(img_array.astype(np.uint8))
    buffer = io.BytesIO()
    img.save(buffer, format=fmt, quality=95)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@router.post("/analyze")
async def analyze_area_endpoint(
    image: UploadFile = File(..., description="Satellite image to analyze"),
    satellite_mode: str = Form("false"),
):
    """
    Analyze an uploaded image for land-cover area measurement.
    Returns JSON with base64-encoded annotated image and area statistics.
    """
    global _latest_result

    if not image.filename or not _allowed_file(image.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    force_satellite = satellite_mode.lower() == "true"

    try:
        from area_measurement.inference import analyze_area
        from fastapi.concurrency import run_in_threadpool

        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        original_array = np.array(img)

        # Offload heavy synchronous inference to a background thread to unblock the main event loop
        result = await run_in_threadpool(analyze_area, img, force_satellite_mode=force_satellite)

        original_b64 = _numpy_to_base64(original_array)
        annotated_b64 = _numpy_to_base64(result["annotated_image"])
        summary_b64 = _numpy_to_base64(result["summary_image"])

        _latest_result = {
            "annotated_image": result["annotated_image"],
            "original_filename": image.filename,
        }

        classes_json = []
        for cls in result["classes"]:
            cls_clean = {
                "class_id": int(cls["class_id"]),
                "class_name": cls["class_name"],
                "color_rgb": list(cls["color_rgb"]),
                "pixel_area": int(cls["pixel_area"]),
                "coverage_percent": float(cls["coverage_percent"]),
                "coverage_tier": cls["coverage_tier"],
                "num_instances": int(cls["num_instances"]),
                "area_m2": float(cls["area_m2"]) if cls["area_m2"] is not None else None,
                "area_hectares": float(cls["area_hectares"]) if cls["area_hectares"] is not None else None,
                "area_km2": float(cls["area_km2"]) if cls["area_km2"] is not None else None,
            }
            classes_json.append(cls_clean)

        return {
            "success": True,
            "original_image": original_b64,
            "annotated_image": annotated_b64,
            "summary_image": summary_b64,
            "classes": classes_json,
            "total_pixels": int(result["total_pixels"]),
            "image_dimensions": result["image_dimensions"],
            "has_physical_area": bool(result["has_physical_area"]),
            "spatial_resolution_m": float(result["spatial_resolution_m"]) if result["spatial_resolution_m"] else None,
            "total_coverage_percent": float(result["total_coverage_percent"]),
            "physical_area_note": result["physical_area_note"],
            "summary_text": result["summary_text"],
            "processing_time_seconds": float(result["processing_time_seconds"]),
            "model_used": result["model_used"],
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/ground")
async def ground_objects_endpoint(
    image: UploadFile = File(..., description="Satellite image for object detection"),
    query: str = Form(..., description="Natural language query, e.g. 'Where are the buildings?'"),
    box_threshold: float = Form(0.3),
):
    """
    Object detection / grounding based on text query.
    Uses Grounding DINO for open-vocabulary detection with tiled inference.
    """
    global _latest_result

    if not image.filename or not _allowed_file(image.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    if not query.strip():
        raise HTTPException(status_code=400, detail="No query provided.")

    try:
        from grounding.api import ground_objects
        from fastapi.concurrency import run_in_threadpool

        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        original_array = np.array(img)

        result = await run_in_threadpool(ground_objects, img, query, box_threshold=box_threshold)

        original_b64 = _numpy_to_base64(original_array)
        annotated_b64 = _numpy_to_base64(result["annotated_image"])

        _latest_result = {
            "annotated_image": result["annotated_image"],
            "original_filename": image.filename,
        }

        return {
            "success": True,
            "query": result["query"],
            "target_label": result.get("target_label", ""),
            "count": result.get("count", 0),
            "detections": result["detections"],
            "original_image": original_b64,
            "annotated_image": annotated_b64,
            "processing_time": result["processing_time"],
            "pipeline_info": result.get("pipeline_info", {}),
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Grounding failed: {str(e)}")


@router.get("/download")
async def download_annotated():
    """Download the latest annotated image as PNG."""
    global _latest_result

    if "annotated_image" not in _latest_result:
        raise HTTPException(status_code=404, detail="No analysis result available.")

    img = Image.fromarray(_latest_result["annotated_image"].astype(np.uint8))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", quality=95)
    buffer.seek(0)

    orig_name = _latest_result.get("original_filename", "image")
    import os
    base_name = os.path.splitext(orig_name)[0]

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{base_name}_area_analysis.png"'},
    )
