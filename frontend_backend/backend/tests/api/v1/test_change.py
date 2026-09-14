import pytest
import os
import rasterio
from fastapi.testclient import TestClient
from app.main import app
import numpy as np

client = TestClient(app)

@pytest.fixture
def make_synthetic_raster(tmp_path):
    def _make_raster(filename, width, height, bands=3, has_square=False, crs='+proj=latlong'):
        path = tmp_path / filename
        data = np.zeros((bands, height, width), dtype=np.uint8)
        if has_square:
            # Add a white square of 50x50 in the middle
            cx, cy = width//2, height//2
            data[:, cy-25:cy+25, cx-25:cx+25] = 255
            
        with rasterio.open(
            str(path),
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=bands,
            dtype=data.dtype,
            crs=crs,
            transform=rasterio.transform.from_origin(10, 10, 1, 1),
        ) as dst:
            dst.write(data)
        return str(path)
    return _make_raster

def upload_raster(path):
    with open(path, "rb") as f:
        resp = client.post("/api/v1/images/upload", files={"file": (os.path.basename(path), f, "image/tiff")})
    return resp.json()["image_id"]

def test_change_analysis_success(make_synthetic_raster):
    before_path = make_synthetic_raster("before.tif", 200, 200, has_square=False)
    after_path = make_synthetic_raster("after.tif", 200, 200, has_square=True)
    
    before_id = upload_raster(before_path)
    after_id = upload_raster(after_path)
    
    resp = client.post("/api/v1/change-analysis", json={
        "before_image_id": before_id,
        "after_image_id": after_id,
        "question": "What changed?"
    })
    
    assert resp.status_code == 200
    data = resp.json()
    
    # 50x50 square = 2500 pixels changed
    assert data["changed_pixel_count"] == 2500
    assert data["change_percentage"] == (2500 / (200*200)) * 100.0
    
    assert data["change_mask"] is not None
    assert data["change_mask"].endswith(".jpg")

def test_change_analysis_incompatible(make_synthetic_raster):
    before_path = make_synthetic_raster("before2.tif", 200, 200, crs='+proj=latlong')
    # different crs
    after_path = make_synthetic_raster("after2.tif", 200, 200, crs='+init=epsg:3857')
    
    before_id = upload_raster(before_path)
    after_id = upload_raster(after_path)
    
    resp = client.post("/api/v1/change-analysis", json={
        "before_image_id": before_id,
        "after_image_id": after_id,
        "question": "What changed?"
    })
    
    # Should fail because images are not aligned
    assert resp.status_code == 400
    assert "Images are not aligned" in resp.json()["detail"]
