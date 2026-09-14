from typing import List, Protocol
from app.schemas.grounding import GroundedObject, BoundingBox
from app.services.image import ImageService

class GroundingModel(Protocol):
    def predict(self, image_id: str, target: str) -> List[GroundedObject]:
        ...

class MockGroundingModel:
    def predict(self, image_id: str, target: str) -> List[GroundedObject]:
        """
        Mock implementation of visual grounding.
        If the target word is found, it returns a deterministic bounding box.
        In a real scenario, this would load the image tensor, run it through a VLM/Grounding DINO, and parse the output.
        """
        # Validate the image actually exists
        img_meta = ImageService.get_image(image_id)
        
        objects = []
        target_lower = target.lower()
        
        if "building" in target_lower:
            objects.append(
                GroundedObject(
                    label="building",
                    confidence=0.91,
                    bbox=BoundingBox(
                        x_min=min(100, img_meta.width - 1),
                        y_min=min(200, img_meta.height - 1),
                        x_max=min(300, img_meta.width),
                        y_max=min(400, img_meta.height)
                    )
                )
            )
            
        if "road" in target_lower:
            objects.append(
                GroundedObject(
                    label="road",
                    confidence=0.88,
                    bbox=BoundingBox(
                        x_min=min(50, img_meta.width - 1),
                        y_min=min(50, img_meta.height - 1),
                        x_max=min(150, img_meta.width),
                        y_max=min(150, img_meta.height)
                    )
                )
            )
            
        return objects
