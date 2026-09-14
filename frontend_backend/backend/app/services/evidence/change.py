import os
import uuid
import glob
import cv2
import numpy as np
import rasterio
from app.core.config import core_settings

class ChangeEvidenceService:
    @staticmethod
    def generate_change_evidence(after_image_id: str, mask: np.ndarray) -> str:
        """
        Draws the binary change mask over the 'after' image as a red highlight.
        Returns the filename of the generated evidence.
        """
        # Find original after image
        search_pattern = os.path.join(core_settings.UPLOAD_DIR, f"{after_image_id}.*")
        matches = glob.glob(search_pattern)
        if not matches:
            raise FileNotFoundError(f"Original image for ID {after_image_id} not found.")
            
        orig_path = matches[0]
        
        # Load the raster data
        with rasterio.open(orig_path) as src:
            num_bands_to_read = min(src.count, 3)
            data = src.read(indexes=tuple(range(1, num_bands_to_read + 1)))
            
        # Convert to (H, W, C)
        img = np.transpose(data, (1, 2, 0))
        
        # Make RGB
        if img.shape[2] == 1:
            img = np.repeat(img, 3, axis=2)
        elif img.shape[2] == 2:
            img = np.pad(img, ((0,0), (0,0), (0,1)), mode='constant')
            
        # Normalize dynamically to 8-bit [0, 255]
        img_min, img_max = np.min(img), np.max(img)
        if img_max > img_min:
            img = (img - img_min) / (img_max - img_min)
            img = (img * 255).astype(np.uint8)
        else:
            img = np.zeros_like(img, dtype=np.uint8)
            
        img = np.ascontiguousarray(img)
            
        # Overlay the mask in Red
        # mask is (H, W) with 1s and 0s
        # Highlight changed pixels by setting their R channel high and lowering G/B
        # Assuming RGB layout currently (which cv2 expects to write out as BGR eventually)
        overlay = img.copy()
        
        # Make it red (index 0 if we write as RGB and cvtColor later, or let's just make index 0 red)
        # Red in RGB is channel 0.
        changed_pixels = mask > 0
        overlay[changed_pixels, 0] = 255
        overlay[changed_pixels, 1] = 0
        overlay[changed_pixels, 2] = 0
        
        # Blend slightly so we can still see the image beneath
        alpha = 0.5
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        evidence_dir = os.path.join(core_settings.UPLOAD_DIR, "evidence")
        os.makedirs(evidence_dir, exist_ok=True)
        
        evidence_filename = f"change_{after_image_id}_{uuid.uuid4().hex[:8]}_evidence.jpg"
        evidence_path = os.path.join(evidence_dir, evidence_filename)
        
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(evidence_path, img_bgr)
        
        return evidence_filename
