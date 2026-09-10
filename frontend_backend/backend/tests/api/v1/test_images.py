import os
import pytest
from fastapi.testclient import TestClient
import rasterio
from rasterio.transform import from_origin
import numpy as np

from app.main import app
from app.core.config import core_settings

client = TestClient(app)

@pytest.fixture
def test_upload_dir(tmp_path):
    """Override the upload directory for testing."""
    original = core_settings.UPLOAD_DIR
    core_settings.UPLOAD_DIR = str(tmp_path)
    yield str(tmp_path)
    core_settings.UPLOAD_DIR = original

@pytest.fixture
def valid_tif_path(tmp_path):
    """Create a valid dummy GeoTIFF for testing."""
    file_path = tmp_path / "test_valid.tif"
    
    # Create a small valid raster
    data = np.zeros((10, 10), dtype=rasterio.uint8)
    transform = from_origin(0, 0, 1, 1)
    
    with rasterio.open(
        file_path,
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(data, 1)
        # Add a tag that identifies it as SAR
        dst.update_tags(TIFFTAG_IMAGEDESCRIPTION="VV polarization")
        
    return str(file_path)

def test_upload_valid_image(test_upload_dir, valid_tif_path):
    with open(valid_tif_path, "rb") as f:
        response = client.post(
            "/api/v1/images/upload",
            files={"file": ("test_valid.tif", f, "image/tiff")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Image uploaded and processed successfully."
    assert "image_id" in data
    
    meta = data["metadata"]
    assert meta["format"] == "tif"
    assert meta["width"] == 10
    assert meta["height"] == 10
    assert meta["bands"] == 1
    assert meta["dtype"] == "uint8"
    assert "crs" in meta

def test_upload_invalid_extension(test_upload_dir, tmp_path):
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("dummy")
    
    with open(invalid_file, "rb") as f:
        response = client.post(
            "/api/v1/images/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
        
    assert response.status_code == 400
    assert response.json()["error"] == "InvalidImageError"

def test_upload_invalid_raster(test_upload_dir, tmp_path):
    invalid_raster = tmp_path / "corrupt.tif"
    invalid_raster.write_text("Not a real raster file")
    
    with open(invalid_raster, "rb") as f:
        response = client.post(
            "/api/v1/images/upload",
            files={"file": ("corrupt.tif", f, "image/tiff")}
        )
        
    assert response.status_code == 422
    assert response.json()["error"] == "RasterProcessingError"

def test_upload_oversized_file(test_upload_dir, valid_tif_path):
    original_size = core_settings.MAX_UPLOAD_SIZE
    core_settings.MAX_UPLOAD_SIZE = 10  # 10 bytes limit
    
    try:
        with open(valid_tif_path, "rb") as f:
            response = client.post(
                "/api/v1/images/upload",
                files={"file": ("test_valid.tif", f, "image/tiff")}
            )
        assert response.status_code == 413
        assert response.json()["error"] == "FileTooLargeError"
    finally:
        core_settings.MAX_UPLOAD_SIZE = original_size

def test_path_traversal_attempt(test_upload_dir, valid_tif_path):
    with open(valid_tif_path, "rb") as f:
        response = client.post(
            "/api/v1/images/upload",
            files={"file": ("../../../etc/passwd.tif", f, "image/tiff")}
        )
        
    assert response.status_code == 400
    assert response.json()["error"] == "PathTraversalError"

def test_get_image(test_upload_dir, valid_tif_path):
    with open(valid_tif_path, "rb") as f:
        upload_resp = client.post(
            "/api/v1/images/upload",
            files={"file": ("S1A_test.tif", f, "image/tiff")}
        )
    assert upload_resp.status_code == 200
    image_id = upload_resp.json()["image_id"]
    
    get_resp = client.get(f"/api/v1/images/{image_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["image_id"] == image_id
    assert "modality_info" in data
    # Should detect SAR because filename contains S1A
    assert data["modality_info"]["modality"] == "SAR"

def test_get_image_not_found(test_upload_dir):
    get_resp = client.get("/api/v1/images/invalid_id_123")
    assert get_resp.status_code == 404
    assert get_resp.json()["error"] == "ImageNotFoundError"
