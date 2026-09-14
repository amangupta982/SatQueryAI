import os
import uuid
import glob
import cv2
import numpy as np
import rasterio
from typing import List
from app.core.config import core_settings
from app.schemas.grounding import GroundedObject

class VisualEvidenceService:
    @staticmethod
    def generate_grounding_evidence(image_id: str, objects: List[GroundedObject]) -> str:
        """
        Draws bounding boxes on the uploaded image and saves it as an evidence artifact.
        Returns the filename of the generated evidence.
        """
        # Find original image
        search_pattern = os.path.join(core_settings.UPLOAD_DIR, f"{image_id}.*")
        matches = glob.glob(search_pattern)
        if not matches:
            raise FileNotFoundError(f"Original image for ID {image_id} not found.")
            
        orig_path = matches[0]
        
        # Load the raster data
        with rasterio.open(orig_path) as src:
            # We only want the first 3 bands for visualization
            num_bands_to_read = min(src.count, 3)
            data = src.read(indexes=tuple(range(1, num_bands_to_read + 1)))
            
        # Rasterio is (C, H, W). Convert to (H, W, C)
        img = np.transpose(data, (1, 2, 0))
        
        # If it's a single band (e.g. SAR), replicate to 3 channels for drawing RGB boxes
        if img.shape[2] == 1:
            img = np.repeat(img, 3, axis=2)
        elif img.shape[2] == 2:
            # Very unusual, but pad with a zero channel
            img = np.pad(img, ((0,0), (0,0), (0,1)), mode='constant')
            
        # Normalize dynamically to 8-bit [0, 255] for cv2 writing
        # This is purely for evidence visualization, NOT for ML processing
        img_min, img_max = np.min(img), np.max(img)
        if img_max > img_min:
            img = (img - img_min) / (img_max - img_min)
            img = (img * 255).astype(np.uint8)
        else:
            img = np.zeros_like(img, dtype=np.uint8)

        # Ensure contiguous array for cv2
        img = np.ascontiguousarray(img)

        # Draw bounding boxes
        for obj in objects:
            box = obj.bbox
            # cv2 format: (img, (x_min, y_min), (x_max, y_max), color, thickness)
            color = (0, 255, 0) # Green box
            cv2.rectangle(
                img,
                (box.x_min, box.y_min),
                (box.x_max, box.y_max),
                color,
                2
            )
            # Put label text above the box
            text = f"{obj.label} ({obj.confidence:.2f})"
            cv2.putText(
                img,
                text,
                (box.x_min, max(box.y_min - 5, 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )
            
        # Save evidence
        evidence_dir = os.path.join(core_settings.UPLOAD_DIR, "evidence")
        os.makedirs(evidence_dir, exist_ok=True)
        
        evidence_filename = f"{image_id}_{uuid.uuid4().hex[:8]}_evidence.jpg"
        evidence_path = os.path.join(evidence_dir, evidence_filename)
        
        # cv2 uses BGR, but if our raster was loaded arbitrarily we might be writing RGB as BGR.
        # This is fine for a rough evidence artifact, but we can try to explicitly assume RGB input and convert.
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(evidence_path, img_bgr)
        
        return evidence_filename
