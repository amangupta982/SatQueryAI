from pydantic import BaseModel, Field
from typing import Optional, Tuple, List, Union

class CropConfig(BaseModel):
    crop_type: str = Field(..., description="'center' or 'random'")
    size: Tuple[int, int] = Field(..., description="(height, width)")

class ResizeConfig(BaseModel):
    target_size: Tuple[int, int] = Field(..., description="(height, width)")
    interpolation: str = Field(default="bilinear", description="'nearest', 'bilinear', 'bicubic'")

class OpticalPreprocessConfig(BaseModel):
    # E.g. [0.1, 0.2, 0.3] for 3 bands
    mean: Optional[List[float]] = None
    std: Optional[List[float]] = None
    # For min/max scaling
    min_val: Optional[Union[float, List[float]]] = None
    max_val: Optional[Union[float, List[float]]] = None
    bands_to_keep: Optional[List[int]] = None
    clip_percentile: Optional[float] = None
    crop: Optional[CropConfig] = None
    resize: Optional[ResizeConfig] = None

class SARPreprocessConfig(BaseModel):
    to_db: bool = Field(default=True, description="Convert amplitude/intensity to Decibels")
    db_min: float = Field(default=-25.0)
    db_max: float = Field(default=0.0)
    bands_to_keep: Optional[List[int]] = None
    crop: Optional[CropConfig] = None
    resize: Optional[ResizeConfig] = None
