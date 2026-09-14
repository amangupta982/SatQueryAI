"""
Unified schemas for SatQuery-VQA training and inference.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    """Normalized bounding box coordinates [ymin, xmin, ymax, xmax] in [0, 1] or [0, 1000]."""
    ymin: float
    xmin: float
    ymax: float
    xmax: float
    label: Optional[str] = None
    confidence: Optional[float] = None

class EvidenceData(BaseModel):
    """Visual or geospatial evidence supporting an answer."""
    bounding_boxes: List[List[float]] = Field(default_factory=list, description="List of [ymin, xmin, ymax, xmax]")
    coverage_tier: Optional[str] = Field(None, description="Primary (>25%), Secondary (5-25%), Marginal (<5%)")
    approx_area_m2: Optional[float] = None
    detected_regions_count: Optional[int] = None
    sensor_bands_used: List[str] = Field(default_factory=list)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

class UnifiedSampleMetadata(BaseModel):
    country: Optional[str] = None
    season: Optional[str] = None
    climate_zone: Optional[str] = None
    lulc_classes: List[str] = Field(default_factory=list)
    split: Optional[str] = None  # 'train', 'val', 'test', 'benchmark'
    source: str = "BigEarthNet.txt"
    format_type: Optional[str] = None  # 'binary', 'mcq', 'caption', 'grounding'
    choices: Optional[List[str]] = None  # For MCQ tasks

class UnifiedVQASample(BaseModel):
    """
    Unified training sample format for SatQuery-VQA adapted to BigEarthNet.txt.
    """
    sample_id: str
    patch_id: str
    image_path: str
    sar_path: Optional[str] = None
    question: str
    answer: str
    task: str  # presence, count, size, adjacency, etc.
    sensor: str = "Sentinel-2"  # 'Sentinel-2', 'Sentinel-1', 'Sentinel-1+2'
    metadata: UnifiedSampleMetadata = Field(default_factory=UnifiedSampleMetadata)
    evidence: EvidenceData = Field(default_factory=EvidenceData)

class VQARequest(BaseModel):
    """API request payload for inference."""
    image_b64: Optional[str] = None
    image_url: Optional[str] = None
    question: str
    sensor_modality: str = "Sentinel-2"

class VQAResponse(BaseModel):
    """API response payload for inference."""
    answer: str
    confidence: Optional[float] = None
    task: str
    model: str = "SatQuery-VQA"
    evidence: Dict[str, Any] = Field(default_factory=dict)
