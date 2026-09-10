from fastapi import APIRouter, HTTPException
import numpy as np
from app.schemas.change import ChangeAnalysisRequest, ChangeDetectionResult
from app.schemas.compatibility import CompatibilityState
from app.services.compatibility import ImageCompatibilityService
from app.services.image import ImageService
from app.services.raster import RasterService
from app.schemas.preprocessing import OpticalPreprocessConfig
from app.services.preprocessing.optical import OpticalPreprocessor
from app.services.preprocessing.tensor import RasterTensorConverter
from app.services.models.change import BaselineChangeModel
from app.services.evidence.change import ChangeEvidenceService
import os
from app.core.config import core_settings
import glob

router = APIRouter(prefix="/change-analysis", tags=["change-analysis"])

model = BaselineChangeModel(threshold=0.2)
preprocessor = OpticalPreprocessor()
converter = RasterTensorConverter()

def load_and_preprocess(image_id: str) -> np.ndarray:
    # Get image file path
    search_pattern = os.path.join(core_settings.UPLOAD_DIR, f"{image_id}.*")
    matches = glob.glob(search_pattern)
    if not matches:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found on disk")
        
    path = matches[0]
    
    import rasterio
    
    # Read raster
    with rasterio.open(path) as src:
        data = src.read()
    
    # Preprocess (min/max scaling using empirical typical values, e.g. 0 to 10000 for optical)
    # We will just normalize to [0, 1] based on actual min/max of the image for robust Baseline CVA
    d_min = float(np.min(data))
    d_max = float(np.max(data))
    
    config = OpticalPreprocessConfig(
        min_val=d_min,
        max_val=d_max
    )
    
    processed = preprocessor.process(data, config)
    return converter.to_tensor(processed)

@router.post("", response_model=ChangeDetectionResult)
async def analyze_change(request: ChangeAnalysisRequest):
    """
    Perform bi-temporal change analysis on two coregistered images.
    """
    # 1. Validate images exist
    img1_meta = ImageService.get_image(request.before_image_id)
    img2_meta = ImageService.get_image(request.after_image_id)
    
    # 2. Check compatibility (must be ALIGNED)
    compat_report = ImageCompatibilityService.compare(img1_meta, img2_meta)
    if compat_report.state in [CompatibilityState.INCOMPATIBLE, CompatibilityState.REQUIRES_REGISTRATION]:
        raise HTTPException(
            status_code=400, 
            detail=f"Images are not aligned. Compatibility state: {compat_report.state.value}"
        )
        
    # 3. Preprocess
    before_tensor = load_and_preprocess(request.before_image_id)
    after_tensor = load_and_preprocess(request.after_image_id)
    
    # Due to some potential differences in bands (e.g. SAR vs Optical), we enforce they have the same band count
    if before_tensor.shape[0] != after_tensor.shape[0]:
         raise HTTPException(
            status_code=400, 
            detail="Images have different number of bands and cannot be compared directly by the baseline model."
        )
        
    # Force spatial dimensions to match precisely if there is a tiny 1-pixel discrepancy due to extents
    if before_tensor.shape != after_tensor.shape:
        min_c = min(before_tensor.shape[0], after_tensor.shape[0])
        min_h = min(before_tensor.shape[1], after_tensor.shape[1])
        min_w = min(before_tensor.shape[2], after_tensor.shape[2])
        before_tensor = before_tensor[:min_c, :min_h, :min_w]
        after_tensor = after_tensor[:min_c, :min_h, :min_w]

    # 4. Run Model
    mask = model.detect_change(before_tensor, after_tensor)
    
    # 5. Statistics
    changed_pixel_count = int(np.sum(mask))
    total_pixels = mask.shape[0] * mask.shape[1]
    change_percentage = (changed_pixel_count / total_pixels) * 100.0 if total_pixels > 0 else 0.0
    
    # 6. Generate Evidence
    evidence_filename = ChangeEvidenceService.generate_change_evidence(
        request.after_image_id, 
        mask
    )
    
    return ChangeDetectionResult(
        change_mask=evidence_filename,
        changed_pixel_count=changed_pixel_count,
        change_percentage=change_percentage,
        confidence=None,
        model_name="BaselineCVA"
    )
