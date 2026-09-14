"""
Data Schemas for Grounding Change & Multitemporal Analysis.
Defines unified dataset sample representation, region structures,
scene representation, query filters, and API outputs.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field, ConfigDict
import numpy as np


class BoundingBox(BaseModel):
    """Bounding box in image pixel coordinates [ymin, xmin, ymax, xmax] or [xmin, ymin, xmax, ymax]."""
    x_min: int
    y_min: int
    x_max: int
    y_max: int

    @property
    def width(self) -> int:
        return max(0, self.x_max - self.x_min)

    @property
    def height(self) -> int:
        return max(0, self.y_max - self.y_min)

    @property
    def area(self) -> int:
        return self.width * self.height


class GeoPoint(BaseModel):
    """Real-world geographic coordinate with projected fallback."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    projected_x: Optional[float] = None
    projected_y: Optional[float] = None
    crs: Optional[str] = None


class GeoSpatialMetadata(BaseModel):
    """Geospatial metadata for an analyzed raster pair."""
    available: bool = False
    crs: Optional[str] = None
    bounds: Optional[List[float]] = None  # [left, bottom, right, top]
    center: Optional[GeoPoint] = None
    transform: Optional[List[float]] = None  # 6-element affine transform
    pixel_resolution: Optional[Tuple[float, float]] = None


class SpectralIndexStats(BaseModel):
    """Temporal statistics for a remote-sensing spectral index (e.g. NDVI, NDWI, NDBI)."""
    available: bool = False
    t1_mean: Optional[float] = None
    t2_mean: Optional[float] = None
    change: Optional[float] = None


class ChangeRegion(BaseModel):
    """
    Fine-grained detected change region.
    No single bounding-box covers the whole scene.
    """
    region_id: str
    category: str
    change_type: str  # added, removed, expanded, reduced, converted
    confidence: float
    bbox: List[int]  # [x_min, y_min, x_max, y_max]
    mask_rle: Optional[str] = None  # Run-length encoded mask string
    centroid_pixel: List[int]  # [col, row]
    area_pixels: int
    area_m2: Optional[float] = None
    geo: Optional[GeoPoint] = None
    t1_dominant_class: Optional[str] = None
    t2_dominant_class: Optional[str] = None


class CategoryStats(BaseModel):
    """Aggregate statistics for a semantic category across the scene."""
    category: str
    t1_area_percent: float
    t2_area_percent: float
    change_percent: float
    direction: str  # increase, decrease, unchanged
    regions_changed: int
    largest_region_pixels: int = 0
    total_changed_pixels: int = 0
    confidence: float = 1.0


class SemanticTransition(BaseModel):
    """Explicit land-cover transition between T1 and T2."""
    from_category: str
    to_category: str
    change_type: str
    pixel_count: int
    percentage: float
    confidence: float = 0.9


class SceneSummary(BaseModel):
    """High-level summary of the detected temporal change."""
    change_detected: bool
    total_scene_pixels: int
    changed_pixels: int
    change_percentage: float
    dominant_changed_category: Optional[str] = None
    largest_changed_region_id: Optional[str] = None
    natural_language_summary: str = ""


class TemporalInfo(BaseModel):
    """Temporal metadata for T1 and T2 acquisitions."""
    t1_timestamp: Optional[str] = None
    t2_timestamp: Optional[str] = None
    interval_days: Optional[int] = None


class VisualEvidence(BaseModel):
    """Filenames or base64 keys of generated visual layers."""
    t1_image: Optional[str] = None
    t2_image: Optional[str] = None
    difference_image: Optional[str] = None
    heatmap: Optional[str] = None
    change_mask: Optional[str] = None
    semantic_change_map: Optional[str] = None
    complete_overlay: Optional[str] = None
    category_overlays: Dict[str, str] = Field(default_factory=dict)
    query_visualization: Optional[str] = None
    legend: Dict[str, Any] = Field(default_factory=dict)


class TemporalChangeScene(BaseModel):
    """
    COMPLETE STRUCTURED CHANGE REPRESENTATION.
    Produced on initial T1+T2 analysis even without a question,
    and stored in session memory for interactive multi-turn querying.
    """
    scene_id: str
    temporal: TemporalInfo = Field(default_factory=TemporalInfo)
    geospatial: GeoSpatialMetadata = Field(default_factory=GeoSpatialMetadata)
    summary: SceneSummary
    categories: Dict[str, CategoryStats] = Field(default_factory=dict)
    regions: List[ChangeRegion] = Field(default_factory=list)
    transitions: List[SemanticTransition] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    spectral_indices: Dict[str, SpectralIndexStats] = Field(default_factory=dict)
    visual_evidence: VisualEvidence = Field(default_factory=VisualEvidence)


class ChangeQueryFilter(BaseModel):
    """Structured filter for querying the scene representation."""
    category: Optional[str] = None
    change_type: Optional[str] = None
    confidence_min: Optional[float] = None
    area_min_pixels: Optional[int] = None
    area_min_m2: Optional[float] = None
    geographic_bounds: Optional[List[float]] = None
    rank_by: Optional[str] = None  # area, confidence, intensity
    top_k: Optional[int] = None


class ChangeAnalysisOutput(BaseModel):
    """Final output response returned to agent, API, and frontend."""
    answer: str
    scene_summary: SceneSummary
    categories: Dict[str, CategoryStats]
    regions: List[ChangeRegion]
    transitions: List[SemanticTransition]
    geospatial: GeoSpatialMetadata
    statistics: Dict[str, Any]
    visualizations: VisualEvidence
    confidence: Dict[str, float]
    provenance: Dict[str, Any] = Field(default_factory=dict)


class TemporalVQASample(BaseModel):
    """
    UNIFIED INTERNAL DATASET SCHEMA.
    All datasets (ChangeChat-105k, RSRCC, QAG-360K, SECOND, BigEarthNet, RSVLM-QA)
    map into this schema with partial supervision support.
    """
    sample_id: str
    image_t1: Union[str, Any]  # Path or array
    image_t2: Optional[Union[str, Any]] = None  # None for single-image VQA
    question: Optional[str] = None
    answer: Optional[str] = None
    timestamp_t1: Optional[str] = None
    timestamp_t2: Optional[str] = None
    change_mask: Optional[Any] = None
    semantic_mask_t1: Optional[Any] = None
    semantic_mask_t2: Optional[Any] = None
    transition_mask: Optional[Any] = None
    grounding_mask: Optional[Any] = None
    bbox_targets: Optional[List[BoundingBox]] = None
    crs: Optional[str] = None
    transform: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)


# =====================================================================
# BigEarthNet.txt Optical-SAR Multimodal Schemas
# (arXiv:2603.29630, txt.bigearth.net)
# =====================================================================

class AnalysisInterpretationMode(str):
    """
    CRITICAL INTERPRETATION DISTINCTION:
    Sentinel-1/Sentinel-2 pairs from BigEarthNet.txt are NOT temporal pairs by default.
    They are same-scene, co-registered two-modality observations.
    """
    MODE_A_CROSS_MODAL = "mode_a_cross_modal"      # Same scene, complementary sensor signatures
    MODE_B_TEMPORAL_CHANGE = "mode_b_temporal_change"  # Activated ONLY when timestamps establish separation


class MultimodalAgentMode(str):
    """The 7 official operating modes of the Optical-SAR Multimodal Agent."""
    MODE_1_OPTICAL_ONLY = "optical_only"
    MODE_2_SAR_ONLY = "sar_only"
    MODE_3_OPTICAL_SAR = "optical_sar"
    MODE_4_OPTICAL_SAR_TEMPORAL = "optical_sar_temporal"
    MODE_5_OPTICAL_SAR_VQA = "optical_sar_vqa"
    MODE_6_OPTICAL_SAR_VQA_GROUNDING = "optical_sar_vqa_grounding"
    MODE_7_OPTICAL_SAR_FULL = "optical_sar_full_geospatial"


class SensorObservationMetadata(BaseModel):
    """Physical acquisition parameters for Sentinel-1 and Sentinel-2 sensors."""
    optical_sensor: str = "Sentinel-2"
    optical_bands: List[str] = Field(default_factory=lambda: ["B02", "B03", "B04", "B8A", "B11", "B12"])
    optical_timestamp: Optional[str] = None
    sar_sensor: str = "Sentinel-1"
    sar_polarizations: List[str] = Field(default_factory=lambda: ["VV", "VH"])
    sar_timestamp: Optional[str] = None
    co_registered: bool = True
    ground_sampling_distance_m: float = 10.0
    country: Optional[str] = None
    season: Optional[str] = None
    climate_zone: Optional[str] = None


class CrossModalDifference(BaseModel):
    """Describes complementary sensor signatures between Optical and SAR."""
    modality_a: str = "Optical (Sentinel-2)"
    modality_b: str = "SAR (Sentinel-1)"
    optical_dominant_features: List[str] = Field(default_factory=list)
    sar_dominant_features: List[str] = Field(default_factory=list)
    cross_modal_correlation: float = 0.0
    complementary_insights: List[str] = Field(default_factory=list)


class BigEarthNetMultimodalSample(BaseModel):
    """
    Unified BigEarthNet.txt multimodal sample representation.
    Covers the 15 tasks across 4 categories:
    Image Captioning, Binary VQA, MCQ VQA, Referring Expression Grounding.
    """
    sample_id: str
    patch_id_optical: str
    patch_id_sar: Optional[str] = None
    optical_image: Union[str, Any]       # Path, GeoTIFF, or numpy tensor (C, H, W)
    sar_image: Optional[Union[str, Any]] = None  # Path, GeoTIFF, or numpy tensor (2, H, W)
    
    # Task annotations
    task_category: str = "vqa"  # captioning, binary, mcq, grounding
    task_name: str = "Presence" # Presence, Area, Counting, Adjacency, Relative Position, etc.
    instruction: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    caption: Optional[str] = None
    referring_expression: Optional[str] = None
    bbox_targets: Optional[List[BoundingBox]] = None
    
    # Geolocation & Metadata
    split: str = "train"  # train, val, test, bench
    sensor_metadata: SensorObservationMetadata = Field(default_factory=SensorObservationMetadata)
    crs: Optional[str] = None
    transform: Optional[List[float]] = None
    bounds: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class OpticalSARScene(BaseModel):
    """Structured perception representation for Optical-SAR multimodal scene."""
    scene_id: str
    interpretation_mode: str = AnalysisInterpretationMode.MODE_A_CROSS_MODAL
    agent_mode: str = MultimodalAgentMode.MODE_7_OPTICAL_SAR_FULL
    sensor_metadata: SensorObservationMetadata
    cross_modal_difference: CrossModalDifference
    categories_detected: List[str] = Field(default_factory=list)
    category_proportions: Dict[str, float] = Field(default_factory=dict)
    grounded_regions: List[ChangeRegion] = Field(default_factory=list)
    vqa_dialogue_history: List[Dict[str, str]] = Field(default_factory=list)
    geospatial: GeoSpatialMetadata = Field(default_factory=GeoSpatialMetadata)
    visual_evidence_paths: Dict[str, str] = Field(default_factory=dict)
    confidence: Dict[str, float] = Field(default_factory=dict)


class OpticalSARAnalysisOutput(BaseModel):
    """Final API / Agent output for Optical-SAR Multimodal Agent."""
    answer: str
    scene: OpticalSARScene
    mode_applied: str
    is_temporal_change: bool
    evidence_urls: Dict[str, str] = Field(default_factory=dict)
    grounded_boxes: List[Dict[str, Any]] = Field(default_factory=list)
    category_summary: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.95
