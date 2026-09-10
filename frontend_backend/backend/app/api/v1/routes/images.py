from fastapi import APIRouter, UploadFile, File
from app.schemas.image import ImageUploadResponse, ImageMetadata
from app.schemas.compatibility import CompareImagesRequest, CompatibilityReport
from app.services.image import ImageService
from app.services.compatibility import ImageCompatibilityService

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a satellite image (GeoTIFF, TIFF, PNG, JPEG).
    Extracts geospatial metadata securely and stores the image.
    """
    return await ImageService.process_upload(file)

@router.post("/compare", response_model=CompatibilityReport)
async def compare_images(request: CompareImagesRequest):
    """
    Compare two uploaded images to evaluate their geospatial compatibility and co-registration.
    """
    img1 = ImageService.get_image(request.image_id_1)
    img2 = ImageService.get_image(request.image_id_2)
    return ImageCompatibilityService.compare(img1, img2)

@router.get("/{image_id}", response_model=ImageMetadata)
async def get_image(image_id: str):
    """
    Retrieve image metadata and detected modality by ID.
    """
    return ImageService.get_image(image_id)

