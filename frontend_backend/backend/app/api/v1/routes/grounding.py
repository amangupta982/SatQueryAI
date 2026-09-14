from fastapi import APIRouter
from app.schemas.grounding import GroundingRequest, GroundingResponse
from app.services.models.grounding import MockGroundingModel
from app.services.evidence.visual import VisualEvidenceService

router = APIRouter(prefix="/grounding", tags=["grounding"])

# Normally this would be injected or instantiated once
model = MockGroundingModel()

@router.post("", response_model=GroundingResponse)
async def predict_grounding(request: GroundingRequest):
    """
    Perform visual grounding/object detection on a given image.
    Uses natural language targets (e.g. 'building', 'road').
    Generates visual evidence bounding boxes.
    """
    objects = model.predict(request.image_id, request.target)
    
    evidence_filename = None
    if objects:
        evidence_filename = VisualEvidenceService.generate_grounding_evidence(
            request.image_id, 
            objects
        )
        
    return GroundingResponse(
        objects=objects,
        evidence_filename=evidence_filename
    )
