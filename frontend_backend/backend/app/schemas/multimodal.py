from pydantic import BaseModel
from typing import Optional, List

class MultimodalRequest(BaseModel):
    optical_image_id: str
    sar_image_id: str
    question: str

class MultimodalResult(BaseModel):
    answer: str
    confidence: Optional[float] = None
    model_name: str
    optical_used: bool
    sar_used: bool
    evidence: List[str]
