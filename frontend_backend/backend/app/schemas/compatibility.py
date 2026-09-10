from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class CompatibilityState(str, Enum):
    ALIGNED = "ALIGNED"
    COMPATIBLE_NOT_VERIFIED = "COMPATIBLE_NOT_VERIFIED"
    REQUIRES_REGISTRATION = "REQUIRES_REGISTRATION"
    INCOMPATIBLE = "INCOMPATIBLE"

class CompareImagesRequest(BaseModel):
    image_id_1: str
    image_id_2: str

class CompatibilityReport(BaseModel):
    state: CompatibilityState
    overlap_percentage_1: Optional[float] = Field(None, description="Percentage of Image 1 overlapping with Image 2")
    overlap_percentage_2: Optional[float] = Field(None, description="Percentage of Image 2 overlapping with Image 1")
    identical_crs: bool = False
    identical_transform: bool = False
    identical_dimensions: bool = False
    resolution_match: bool = False
    reasoning: str
