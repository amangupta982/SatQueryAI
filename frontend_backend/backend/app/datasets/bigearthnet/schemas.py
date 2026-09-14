from pydantic import BaseModel, Field
from typing import List, Optional

class AnnotationRecord(BaseModel):
    id: int = Field(alias="ID")
    s1_name: str
    patch_id: str
    input: str
    output: str
    type: str
    category: str
    split: str
    latitude: float
    longitude: float
    country: str
    season: str
    climate_zone: str

class ManifestRecord(BaseModel):
    pair_id: str
    sentinel1_id: str
    sentinel2_id: str
    optical_path: str
    sar_path: str
    latitude: float
    longitude: float
    country: str
    season: str
    climate_zone: str
    split: str
    annotation_count: int
    tasks: List[str]

class SelectedAnnotation(BaseModel):
    pair_id: str
    input: str
    output: str
    type: str
    category: str
    split: str
    original_id: int
