from fastapi import APIRouter, HTTPException
import numpy as np
import os
import glob
import rasterio

from app.schemas.multimodal import MultimodalRequest, MultimodalResult
from app.schemas.compatibility import CompatibilityState
from app.schemas.image import ImageModality
from app.services.compatibility import ImageCompatibilityService
from app.services.image import ImageService
from app.services.modality import ModalityDetectionService
from app.services.preprocessing.optical import OpticalPreprocessor
from app.services.preprocessing.sar import SARPreprocessor
from app.schemas.preprocessing import OpticalPreprocessConfig, SARPreprocessConfig
from app.services.preprocessing.tensor import RasterTensorConverter
from app.services.models.multimodal import MockOpticalSARModel
from app.services.evidence.multimodal import MultimodalEvidenceService
from app.core.config import core_settings

router = APIRouter(prefix="/multimodal", tags=["multimodal"])

model = MockOpticalSARModel()
opt_preprocessor = OpticalPreprocessor()
sar_preprocessor = SARPreprocessor()
converter = RasterTensorConverter()

def read_raster_data(image_id: str) -> np.ndarray:
    search_pattern = os.path.join(core_settings.UPLOAD_DIR, f"{image_id}.*")
    matches = glob.glob(search_pattern)
    if not matches:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found on disk")
        
    path = matches[0]
    with rasterio.open(path) as src:
        data = src.read()
    return data

@router.post("/optical-sar", response_model=MultimodalResult)
async def analyze_optical_sar(request: MultimodalRequest):
    """
    Perform multimodal analysis on an Optical and SAR image pair.
    """
    # 1. Validate images exist
    opt_meta = ImageService.get_image(request.optical_image_id)
    sar_meta = ImageService.get_image(request.sar_image_id)
    
    # 2. Confirm Modalities
    opt_modality_res = ModalityDetectionService.detect_modality(opt_meta.model_dump(), opt_meta.filename)
    sar_modality_res = ModalityDetectionService.detect_modality(sar_meta.model_dump(), sar_meta.filename)
    
    if opt_modality_res.modality not in [ImageModality.OPTICAL, ImageModality.MULTISPECTRAL]:
        raise HTTPException(
            status_code=400, 
            detail=f"optical_image_id {request.optical_image_id} is not classified as OPTICAL. Detected: {opt_modality_res.modality}"
        )
        
    if sar_modality_res.modality != ImageModality.SAR:
        raise HTTPException(
            status_code=400, 
            detail=f"sar_image_id {request.sar_image_id} is not classified as SAR. Detected: {sar_modality_res.modality}"
        )
        
    # 3. Check compatibility (CRS, geographic overlap, resolution, dimensions)
    compat_report = ImageCompatibilityService.compare(opt_meta, sar_meta)
    if compat_report.state in [CompatibilityState.INCOMPATIBLE, CompatibilityState.REQUIRES_REGISTRATION]:
        raise HTTPException(
            status_code=400, 
            detail=f"Images are not aligned. Compatibility state: {compat_report.state.value}"
        )
        
    # 4. Load & Preprocess separately
    opt_data = read_raster_data(request.optical_image_id)
    sar_data = read_raster_data(request.sar_image_id)
    
    # Simple configs for mock
    opt_config = OpticalPreprocessConfig(
        min_val=float(np.min(opt_data)), 
        max_val=float(np.max(opt_data))
    )
    
    sar_config = SARPreprocessConfig(
        min_db=-30.0,
        max_db=0.0
    )
    
    opt_processed = opt_preprocessor.process(opt_data, opt_config)
    sar_processed = sar_preprocessor.process(sar_data, sar_config)
    
    opt_tensor = converter.to_tensor(opt_processed)
    sar_tensor = converter.to_tensor(sar_processed)
    
    # Force precise spatial dims if tiny 1px diff
    if opt_tensor.shape[1:] != sar_tensor.shape[1:]:
        min_h = min(opt_tensor.shape[1], sar_tensor.shape[1])
        min_w = min(opt_tensor.shape[2], sar_tensor.shape[2])
        opt_tensor = opt_tensor[:, :min_h, :min_w]
        sar_tensor = sar_tensor[:, :min_h, :min_w]
        
    # 5. Model Inference
    answer = model.predict(opt_tensor, sar_tensor, request.question)
    
    # 6. Generate Evidence
    evidence_filename = MultimodalEvidenceService.generate_evidence(
        request.optical_image_id, 
        request.sar_image_id
    )
    
    return MultimodalResult(
        answer=answer,
        confidence=None,
        model_name="MockOpticalSARModel",
        optical_used=True,
        sar_used=True,
        evidence=[evidence_filename]
    )
