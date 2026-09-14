"""
Agent Tool Dispatcher Interface.
Exposes standard callable tool interfaces for the SatQueryAI agent:
- analyze_temporal_scene
- filter_changes
- rank_changes
- get_region
- get_category_statistics
- get_geographic_location
- render_change_layer
- export_geojson
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image

from ..schemas import (
    ChangeAnalysisOutput,
    ChangeQueryFilter,
    ChangeRegion,
    GeoSpatialMetadata,
)
from .pipeline import ChangeInferencePipeline
from .session import session_manager
from .query_engine import ChangeQueryEngine
from .geojson_export import GeoJSONExporter


# Global pipeline instance initialized on demand
_pipeline_instance: Optional[ChangeInferencePipeline] = None


def _get_pipeline() -> ChangeInferencePipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = ChangeInferencePipeline()
    return _pipeline_instance


def analyze_temporal_scene(
    image_t1: Union[str, Path, np.ndarray, Image.Image],
    image_t2: Union[str, Path, np.ndarray, Image.Image],
    question: Optional[str] = None,
    timestamps: Optional[Tuple[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    return_visuals: bool = True,
    return_geo: bool = True,
) -> ChangeAnalysisOutput:
    """
    Primary Agent Tool:
    Builds the complete scene representation and answers any question.
    """
    geo_meta = None
    if metadata:
        geo_meta = GeoSpatialMetadata(
            available=metadata.get("geospatial_available", False),
            crs=metadata.get("crs"),
            bounds=metadata.get("bounds"),
            transform=metadata.get("transform"),
            pixel_resolution=metadata.get("resolution") or metadata.get("pixel_resolution")
        )

    pipeline = _get_pipeline()
    return pipeline.analyze(
        image_t1=image_t1,
        image_t2=image_t2,
        question=question,
        timestamps=timestamps,
        geospatial_meta=geo_meta,
        session_id=session_id,
        return_visuals=return_visuals,
        return_geo=return_geo
    )


def query_temporal_scene(session_id: str, question: str) -> Dict[str, Any]:
    """
    Agent Tool for follow-up conversational turns.
    Queries the persistent session representation without re-running models.
    """
    pipeline = _get_pipeline()
    return pipeline.query_session(session_id=session_id, question=question)


def filter_changes(
    session_id: str,
    category: Optional[str] = None,
    change_type: Optional[str] = None,
    confidence_min: Optional[float] = None,
    area_min_pixels: Optional[int] = None,
    area_min_m2: Optional[float] = None,
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Filters detected changes stored in session memory.
    """
    state = session_manager.get_session(session_id)
    if not state:
        return []

    q_filter = ChangeQueryFilter(
        category=category,
        change_type=change_type,
        confidence_min=confidence_min,
        area_min_pixels=area_min_pixels,
        area_min_m2=area_min_m2,
        top_k=top_k
    )
    filtered = ChangeQueryEngine.filter_regions(state.scene, q_filter)
    session_manager.update_active_selection(session_id, filtered, category=category, change_type=change_type)
    return [r.model_dump() for r in filtered]


def rank_changes(
    session_id: str,
    by: str = "area",
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Ranks changes by 'area', 'confidence', or 'intensity'.
    """
    state = session_manager.get_session(session_id)
    if not state:
        return []

    q_filter = ChangeQueryFilter(rank_by=by, top_k=top_k)
    ranked = ChangeQueryEngine.filter_regions(state.scene, q_filter)
    return [r.model_dump() for r in ranked]


def get_region(session_id: str, region_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns full details for a single discrete change region.
    """
    state = session_manager.get_session(session_id)
    if not state:
        return None

    for r in state.scene.regions:
        if r.region_id.upper() == region_id.upper():
            return r.model_dump()
    return None


def get_category_statistics(session_id: str, category: str) -> Optional[Dict[str, Any]]:
    """
    Returns area before, area after, delta, and region count for a category.
    """
    state = session_manager.get_session(session_id)
    if not state:
        return None

    cat_clean = category.lower().strip()
    stats = state.scene.categories.get(cat_clean)
    return stats.model_dump() if stats else None


def get_geographic_location(session_id: str, region_id: str) -> Dict[str, Any]:
    """
    Retrieves geographic latitude/longitude coordinates and projected coordinates for a region.
    """
    state = session_manager.get_session(session_id)
    if not state:
        return {"error": f"Session {session_id} not found."}

    for r in state.scene.regions:
        if r.region_id.upper() == region_id.upper():
            if r.geo and r.geo.latitude is not None and r.geo.longitude is not None:
                return {
                    "region_id": r.region_id,
                    "geospatial_available": True,
                    "latitude": r.geo.latitude,
                    "longitude": r.geo.longitude,
                    "projected_x": r.geo.projected_x,
                    "projected_y": r.geo.projected_y,
                    "crs": r.geo.crs
                }
            return {
                "region_id": r.region_id,
                "geospatial_available": False,
                "coordinate_type": "image_pixel",
                "pixel_location": {"centroid_pixel": r.centroid_pixel, "bbox": r.bbox}
            }

    return {"error": f"Region {region_id} not found."}


def export_geojson(session_id: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Exports all detected regions in the session to a GeoJSON FeatureCollection.
    """
    state = session_manager.get_session(session_id)
    if not state:
        return {"error": f"Session {session_id} not found."}

    path = Path(output_path) if output_path else None
    return GeoJSONExporter.export_scene_to_geojson(state.scene, output_path=path)


# =====================================================================
# Optical-SAR Multimodal Agent Tool Dispatchers (BigEarthNet.txt)
# =====================================================================

_optical_sar_pipeline_instance = None


def _get_optical_sar_pipeline():
    global _optical_sar_pipeline_instance
    if _optical_sar_pipeline_instance is None:
        from .optical_sar_pipeline import OpticalSARInferencePipeline
        _optical_sar_pipeline_instance = OpticalSARInferencePipeline()
    return _optical_sar_pipeline_instance


def analyze_optical_sar_scene(
    optical_image: Union[str, Path, np.ndarray, Image.Image],
    sar_image: Optional[Union[str, Path, np.ndarray, Image.Image]] = None,
    question: Optional[str] = None,
    referring_expression: Optional[str] = None,
    optical_timestamp: Optional[str] = None,
    sar_timestamp: Optional[str] = None,
    agent_mode: str = "optical_sar_full_geospatial",
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Primary Optical-SAR Agent Tool:
    Ingests co-registered Sentinel-1 SAR + Sentinel-2 Optical observations,
    performs cross-modal fusion, VQA reasoning, and visual grounding.
    """
    pipeline = _get_optical_sar_pipeline()
    result = pipeline.analyze(
        optical_input=optical_image,
        sar_input=sar_image,
        question=question,
        referring_expression=referring_expression,
        optical_timestamp=optical_timestamp,
        sar_timestamp=sar_timestamp,
        agent_mode=agent_mode,
        geospatial_meta=metadata
    )
    from .optical_sar_reasoner import optical_sar_sessions
    optical_sar_sessions.save_scene(result.scene)
    return result


def query_optical_sar_scene(session_id: str, question: str) -> Dict[str, Any]:
    """
    Interactive conversational query on a cached OpticalSARScene.
    """
    from .optical_sar_reasoner import optical_sar_sessions, OpticalSARReasoner
    scene = optical_sar_sessions.get_scene(session_id)
    if not scene:
        return {"error": f"Optical-SAR Session {session_id} not found."}
    response = OpticalSARReasoner.answer_query(scene, question)
    optical_sar_sessions.add_dialogue(session_id, question, response["answer"])
    return response


def get_supported_agent_modes() -> List[Dict[str, str]]:
    """Returns the 7 operational modes supported by the Optical-SAR Agent."""
    return [
        {"mode": "optical_only", "description": "Mode 1: Sentinel-2 Multispectral foundation analysis only."},
        {"mode": "sar_only", "description": "Mode 2: Sentinel-1 SAR radar backscatter analysis only."},
        {"mode": "optical_sar", "description": "Mode 3: Joint Optical + SAR cross-modal alignment and fusion."},
        {"mode": "optical_sar_temporal", "description": "Mode 4: Optical + SAR with explicit temporal metadata verification."},
        {"mode": "optical_sar_vqa", "description": "Mode 5: Optical + SAR with 15 BigEarthNet.txt VQA task reasoning."},
        {"mode": "optical_sar_vqa_grounding", "description": "Mode 6: Optical + SAR VQA plus referring expression spatial bounding box grounding."},
        {"mode": "optical_sar_full_geospatial", "description": "Mode 7: Complete pipeline with local EPSG/WGS84 projection coordinates."}
    ]

