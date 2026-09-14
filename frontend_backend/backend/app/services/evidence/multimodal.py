import os
import uuid
import glob
import cv2
import numpy as np
import rasterio
from app.core.config import core_settings

class MultimodalEvidenceService:
    @staticmethod
    def _load_as_8bit_rgb(image_id: str, is_sar: bool = False) -> np.ndarray:
        search_pattern = os.path.join(core_settings.UPLOAD_DIR, f"{image_id}.*")
        matches = glob.glob(search_pattern)
        if not matches:
            raise FileNotFoundError(f"Original image for ID {image_id} not found.")
            
        orig_path = matches[0]
        
        with rasterio.open(orig_path) as src:
            num_bands = min(src.count, 3)
            data = src.read(indexes=tuple(range(1, num_bands + 1)))
            
        img = np.transpose(data, (1, 2, 0))
        
        # Convert to 8-bit dynamic range
        if is_sar:
            # For SAR visualization, usually dB scaling is better, but here we just MinMax for visual
            # Since raw SAR can have high dynamic range, log scale it for the visual
            img = np.log10(np.clip(img, 1e-5, None))
            
        img_min, img_max = np.min(img), np.max(img)
        if img_max > img_min:
            img = (img - img_min) / (img_max - img_min)
            img = (img * 255).astype(np.uint8)
        else:
            img = np.zeros_like(img, dtype=np.uint8)
            
        if img.shape[2] == 1:
            img = np.repeat(img, 3, axis=2)
        elif img.shape[2] == 2:
            img = np.pad(img, ((0,0), (0,0), (0,1)), mode='constant')
            
        return np.ascontiguousarray(img)

    @staticmethod
    def generate_evidence(optical_image_id: str, sar_image_id: str) -> str:
        """
        Generates a 3-panel panoramic evidence artifact:
        [Optical RGB] | [SAR Grayscale] | [Fused False-Color]
        """
        opt_img = MultimodalEvidenceService._load_as_8bit_rgb(optical_image_id, is_sar=False)
        sar_img = MultimodalEvidenceService._load_as_8bit_rgb(sar_image_id, is_sar=True)
        
        # Ensure dimensions match for the visual (in case of slight 1 pixel off)
        min_h = min(opt_img.shape[0], sar_img.shape[0])
        min_w = min(opt_img.shape[1], sar_img.shape[1])
        
        opt_img = opt_img[:min_h, :min_w]
        sar_img = sar_img[:min_h, :min_w]
        
        # Create Fused False-Color (R: SAR, G: Opt Green, B: Opt Blue)
        fused = np.zeros_like(opt_img)
        fused[:, :, 0] = sar_img[:, :, 0] # SAR to Red
        fused[:, :, 1] = opt_img[:, :, 1] # Opt Green
        fused[:, :, 2] = opt_img[:, :, 2] # Opt Blue
        
        # Add labels
        def add_label(img, text):
            cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
        add_label(opt_img, "Optical (RGB)")
        add_label(sar_img, "SAR (Amplitude)")
        add_label(fused, "Fused (R:SAR G:Opt B:Opt)")
        
        # Stitch horizontally
        stitched = np.hstack((opt_img, sar_img, fused))
        
        evidence_dir = os.path.join(core_settings.UPLOAD_DIR, "evidence")
        os.makedirs(evidence_dir, exist_ok=True)
        
        evidence_filename = f"multimodal_{optical_image_id[:8]}_{sar_image_id[:8]}_{uuid.uuid4().hex[:4]}.jpg"
        evidence_path = os.path.join(evidence_dir, evidence_filename)
        
        # Write out
        stitched_bgr = cv2.cvtColor(stitched, cv2.COLOR_RGB2BGR)
        cv2.imwrite(evidence_path, stitched_bgr)
        
        return evidence_filename
