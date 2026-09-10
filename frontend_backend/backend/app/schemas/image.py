from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ImageModality(str, Enum):
    OPTICAL = "OPTICAL"
    MULTISPECTRAL = "MULTISPECTRAL"
    SAR = "SAR"
    UNKNOWN = "UNKNOWN"

class ModalityDetectionResult(BaseModel):
    modality: ImageModality
    confidence: Optional[float] = None
    reason: str

class ImageMetadata(BaseModel):
    """Metadata extracted from a satellite image (e.g. GeoTIFF)."""
    image_id: str
    filename: str
    format: str
    width: int
    height: int
    bands: int
    dtype: str
    crs: Optional[str] = None
    transform: Optional[List[float]] = None
    bounds: Optional[List[float]] = None
    resolution: Optional[List[float]] = None
    driver: Optional[str] = None
    raster_metadata: Optional[dict] = Field(default_factory=dict)
    modality_info: Optional[ModalityDetectionResult] = None

class ImageUploadResponse(BaseModel):
    """Response returned upon successful image upload."""
    message: str = "Image uploaded and processed successfully."
    image_id: str
    metadata: ImageMetadata
