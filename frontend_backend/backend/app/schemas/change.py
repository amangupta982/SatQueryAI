from pydantic import BaseModel
from typing import Optional

class ChangeAnalysisRequest(BaseModel):
    before_image_id: str
    after_image_id: str
    question: str

class ChangeDetectionResult(BaseModel):
    change_mask: str
    changed_pixel_count: int
    change_percentage: float
    confidence: Optional[float] = None
    model_name: str
