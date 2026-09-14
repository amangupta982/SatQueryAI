import os
import uuid
import shutil
import glob
from fastapi import UploadFile
from app.core.config import core_settings
from app.core.exceptions import ImageNotFoundError
from app.schemas.image import ImageUploadResponse, ImageMetadata
from app.services.file_validation import FileValidationService
from app.services.raster import RasterService
from app.services.modality import ModalityDetectionService

class ImageService:
    @staticmethod
    async def process_upload(file: UploadFile) -> ImageUploadResponse:
        """
        Validates, saves, and extracts metadata for an uploaded image.
        """
        # 1. Validation
        await FileValidationService.validate_upload(file)

        # 2. Generate unique IDs and paths
        image_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1].lower()
        secure_filename = f"{image_id}{ext}"
        
        # Ensure upload directory exists
        os.makedirs(core_settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(core_settings.UPLOAD_DIR, secure_filename)

        # 3. Save file securely
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            file.file.close()

        # 4. Extract raster metadata
        raster_meta = RasterService.extract_metadata(file_path)

        # 5. Detect modality
        modality_info = ModalityDetectionService.detect_modality(raster_meta, file.filename)

        # 6. Build response
        metadata = ImageMetadata(
            image_id=image_id,
            filename=file.filename,
            format=ext.lstrip('.'),
            modality_info=modality_info,
            **raster_meta
        )

        return ImageUploadResponse(
            image_id=image_id,
            metadata=metadata
        )

    @staticmethod
    def get_image(image_id: str) -> ImageMetadata:
        """
        Retrieves metadata and modality for a previously uploaded image.
        Since we lack a database, this dynamically resolves the file on disk.
        """
        # Search for any file in UPLOAD_DIR starting with image_id
        search_pattern = os.path.join(core_settings.UPLOAD_DIR, f"{image_id}.*")
        matches = glob.glob(search_pattern)
        
        if not matches:
            raise ImageNotFoundError(f"Image with ID {image_id} could not be found.")
            
        file_path = matches[0]
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Extract metadata dynamically
        raster_meta = RasterService.extract_metadata(file_path)
        modality_info = ModalityDetectionService.detect_modality(raster_meta, filename)
        
        return ImageMetadata(
            image_id=image_id,
            filename=filename,
            format=ext.lstrip('.'),
            modality_info=modality_info,
            **raster_meta
        )
