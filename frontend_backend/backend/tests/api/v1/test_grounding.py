import pytest
import os
import rasterio
from fastapi.testclient import TestClient
from app.main import app
import numpy as np

client = TestClient(app)

@pytest.fixture
def make_synthetic_raster(tmp_path):
    def _make_raster(filename, width, height, bands=3):
        path = tmp_path / filename
        data = np.zeros((bands, height, width), dtype=np.uint8)
        # Just put some values
        data[0, :, :] = 100
        with rasterio.open(
            str(path),
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=bands,
            dtype=data.dtype,
            crs='+proj=latlong',
            transform=rasterio.transform.from_origin(10, 10, 1, 1),
        ) as dst:
            dst.write(data)
        return str(path)
    return _make_raster

def upload_raster(path):
    with open(path, "rb") as f:
        resp = client.post("/api/v1/images/upload", files={"file": (os.path.basename(path), f, "image/tiff")})
    return resp.json()["image_id"]

def test_grounding_endpoint(make_synthetic_raster):
    # Create 500x500 image
    img_path = make_synthetic_raster("test_grounding.tif", 500, 500, bands=3)
    image_id = upload_raster(img_path)
    
    # Target that matches our mock
    resp = client.post("/api/v1/grounding", json={"image_id": image_id, "target": "find building"})
    assert resp.status_code == 200
    data = resp.json()
    
    assert len(data["objects"]) == 1
    obj = data["objects"][0]
    assert obj["label"] == "building"
    assert obj["confidence"] == 0.91
    assert obj["bbox"]["x_min"] == 100
    
    # Verify evidence was generated
    evidence_file = data["evidence_filename"]
    assert evidence_file is not None
    assert evidence_file.endswith(".jpg")
    
    # Check if the file actually exists
    from app.core.config import core_settings
    evidence_path = os.path.join(core_settings.UPLOAD_DIR, "evidence", evidence_file)
    assert os.path.exists(evidence_path)

def test_grounding_no_match(make_synthetic_raster):
    img_path = make_synthetic_raster("test_grounding_no_match.tif", 500, 500, bands=1)
    image_id = upload_raster(img_path)
    
    resp = client.post("/api/v1/grounding", json={"image_id": image_id, "target": "water"})
    assert resp.status_code == 200
    data = resp.json()
    
    assert len(data["objects"]) == 0
    assert data["evidence_filename"] is None
