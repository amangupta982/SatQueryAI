"""
FastAPI Router for SatQuery-VQA inference endpoint.
Provides POST /api/v1/vqa for natural language satellite image question answering.
"""

import io
import base64
import logging
from typing import Optional
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from pydantic import BaseModel, Field
from PIL import Image

from vqa_captioning.inference.predictor import SatQueryPredictor
from common.schemas.vqa import VQARequest, VQAResponse

from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Visual Question Answering"])

# Global singleton predictor instance and loading state
_vqa_predictor: Optional[SatQueryPredictor] = None
_vqa_load_error: Optional[str] = None
_vqa_is_loading: bool = False

def get_vqa_predictor() -> Optional[SatQueryPredictor]:
    """Dependency injection to provide or initialize SatQueryPredictor."""
    global _vqa_predictor, _vqa_load_error, _vqa_is_loading
    if _vqa_predictor is None and not _vqa_is_loading:
        _vqa_is_loading = True
        adapter_dir = Path("models/satquery-vqa/adapter")
        adapter_path = str(adapter_dir) if adapter_dir.exists() and (adapter_dir / "adapter_config.json").exists() else None

        logger.info(f"[VQA] Initializing SatQueryPredictor (adapter={adapter_path})...")
        try:
            _vqa_predictor = SatQueryPredictor(
                model_name_or_path="Qwen/Qwen2.5-VL-3B-Instruct",
                adapter_path=adapter_path,
            )
            _vqa_load_error = None
            logger.info("[VQA] SatQueryPredictor successfully initialized.")
        except Exception as e:
            _vqa_load_error = str(e)
            logger.error(f"[VQA] ERROR: Failed to initialize SatQueryPredictor: {e}")
            _vqa_predictor = None
        finally:
            _vqa_is_loading = False

    return _vqa_predictor

@router.get("/vqa/status")
async def vqa_model_status():
    """
    Returns authentic model status.
    Possible states: loaded, loading, unavailable
    """
    global _vqa_predictor, _vqa_load_error, _vqa_is_loading

    adapter_dir = Path("models/satquery-vqa/adapter")
    adapter_exists = adapter_dir.exists() and (adapter_dir / "adapter_config.json").exists()
    vlanet_weights = Path("models/satquery-vqa/satquery_vlanet.pt")

    if _vqa_predictor is None and not _vqa_is_loading:
        get_vqa_predictor()

    model_obj = _vqa_predictor.model if _vqa_predictor else None
    is_loaded = model_obj is not None and (
        getattr(model_obj, "vlanet", None) is not None or getattr(model_obj, "model", None) is not None
    )

    if _vqa_is_loading:
        status = "loading"
    elif is_loaded:
        status = "loaded"
    else:
        status = "unavailable"

    return {
        "status": status,
        "model": "SatQuery-VQA",
        "architecture": "SatQueryVLANet" if getattr(model_obj, "vlanet", None) is not None else "Qwen-VL",
        "adapter_path": str(adapter_dir) if adapter_exists else str(vlanet_weights) if vlanet_weights.exists() else None,
        "adapter_exists": adapter_exists or vlanet_weights.exists(),
        "is_loaded": is_loaded,
        "error": _vqa_load_error,
    }

@router.post("/vqa", response_model=VQAResponse)
async def visual_question_answering(
    question: str = Form(..., description="Natural language question about the satellite scene"),
    image: Optional[UploadFile] = File(None, description="Uploaded satellite image file (PNG/JPEG/TIFF)"),
    image_b64: Optional[str] = Form(None, description="Optional Base64-encoded image string"),
    image_id: Optional[str] = Form(None, description="Optional preset image identifier (e.g. 'brahmaputra')"),
    sensor: str = Form("Sentinel-2", description="Modality: Sentinel-2 (optical) or Sentinel-1 (SAR)"),
):
    """
    Satellite Visual Question Answering Endpoint.
    Takes an image (multipart upload or base64 or preset image_id) and natural language question.
    Returns: answer, confidence (non-fabricated), task, evidence, model.
    """
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    predictor = get_vqa_predictor()
    model_obj = predictor.model if predictor else None
    has_model = model_obj is not None and (
        getattr(model_obj, "vlanet", None) is not None or getattr(model_obj, "model", None) is not None
    )
    if not has_model:
        raise HTTPException(
            status_code=503,
            detail=(
                "SatQuery-VQA model is currently unavailable. "
                "The genuine vision-language model checkpoint is not loaded on this backend."
            ),
        )

    pil_image = None

    # 1. Parse image from Multipart UploadFile
    if image is not None:
        try:
            image_bytes = await image.read()
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file upload: {str(e)}")

    # 2. Parse image from Base64 string if provided
    elif image_b64 is not None and image_b64.strip():
        try:
            b64_data = image_b64.split(",")[-1]
            image_bytes = base64.b64decode(b64_data)
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")

    # 3. Parse image from known preset / public scenes if image_id provided
    elif image_id is not None:
        preset_map = {
            "brahmaputra": "hero_brahmaputra_exact_seamless.jpg",
            "bengaluru": "satellite_scene.jpg",
            "inundation": "cap_optical_sar.jpg",
        }
        filename = preset_map.get(image_id, "hero_brahmaputra_exact_seamless.jpg")
        public_path = Path(__file__).resolve().parent.parent / "frontend" / "public" / filename
        if public_path.exists():
            try:
                pil_image = Image.open(public_path).convert("RGB")
            except Exception:
                pass

    if pil_image is None:
        raise HTTPException(
            status_code=400,
            detail="An image must be provided either via multipart file upload ('image') or base64 string ('image_b64').",
        )

    # Logging per development transparency requirement
    logger.info(f"[VQA] Image loaded: dimensions={pil_image.size}, sensor={sensor}")
    logger.info(f"[VQA] Question received: '{question}'")
    logger.info("[VQA] Processor executed")
    logger.info(f"[VQA] Model: SatQuery-VQA")
    logger.info(f"[VQA] Adapter: {predictor.model.adapter_path or 'Base Qwen2.5-VL-3B'}")
    logger.info("[VQA] Generation started")

    try:
        from fastapi.concurrency import run_in_threadpool
        result = await run_in_threadpool(
            predictor.ask,
            image=pil_image,
            question=question,
            sensor=sensor,
        )
        logger.info("[VQA] Generation completed")
        logger.info(f"[VQA] Raw model output: '{result.get('answer')}'")

        return VQAResponse(
            answer=result["answer"],
            confidence=result.get("confidence"),
            task=result.get("task", "vqa"),
            model=result.get("model", "SatQuery-VQA"),
            evidence=result.get("evidence", {}),
        )
    except Exception as e:
        logger.error(f"[VQA] ERROR: Inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")
