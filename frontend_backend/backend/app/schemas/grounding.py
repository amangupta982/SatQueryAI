from pydantic import BaseModel
from typing import List, Optional

class BoundingBox(BaseModel):
    x_min: int
    y_min: int
    x_max: int
    y_max: int

class GroundedObject(BaseModel):
    label: str
    confidence: float
    bbox: BoundingBox

class GroundingRequest(BaseModel):
    image_id: str
    target: str

class GroundingResponse(BaseModel):
    objects: List[GroundedObject]
    evidence_filename: Optional[str] = None
