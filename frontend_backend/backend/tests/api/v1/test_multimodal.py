import pytest
import os
import rasterio
import numpy as np
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def make_synthetic_raster(tmp_path):
    def _make_raster(filename, width, height, bands, crs='+proj=latlong', tags=None):
        path = tmp_path / filename
        data = np.zeros((bands, height, width), dtype=np.uint8)
        
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
            if tags:
                dst.update_tags(**tags)
        return str(path)
    return _make_raster

def upload_raster(path):
    with open(path, "rb") as f:
        resp = client.post("/api/v1/images/upload", files={"file": (os.path.basename(path), f, "image/tiff")})
    return resp.json()["image_id"]

def test_multimodal_analysis_success(make_synthetic_raster):
    # Create optical (3 bands)
    opt_path = make_synthetic_raster("S2A_optical.tif", 100, 100, bands=3)
    # Create SAR (1 band, add polarization tag to trigger heuristic)
    sar_path = make_synthetic_raster("S1A_sar.tif", 100, 100, bands=1, tags={'polarization': 'VV'})
    
    opt_id = upload_raster(opt_path)
    sar_id = upload_raster(sar_path)
    
    resp = client.post("/api/v1/multimodal/optical-sar", json={
        "optical_image_id": opt_id,
        "sar_image_id": sar_id,
        "question": "Are there buildings?"
    })
    
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["optical_used"] is True
    assert data["sar_used"] is True
    assert "optical data" in data["answer"]
    assert "SAR amplitude" in data["answer"]
    assert "Are there buildings?" in data["answer"]
    
    assert len(data["evidence"]) == 1
    assert data["evidence"][0].endswith(".jpg")

def test_multimodal_analysis_invalid_modalities(make_synthetic_raster):
    # Two optical images
    opt1_path = make_synthetic_raster("S2A_opt1.tif", 100, 100, bands=3)
    opt2_path = make_synthetic_raster("S2A_opt2.tif", 100, 100, bands=3)
    
    opt1_id = upload_raster(opt1_path)
    opt2_id = upload_raster(opt2_path)
    
    resp = client.post("/api/v1/multimodal/optical-sar", json={
        "optical_image_id": opt1_id,
        "sar_image_id": opt2_id, # passing optical as SAR
        "question": "test"
    })
    
    assert resp.status_code == 400
    assert "not classified as SAR" in resp.json()["detail"]

def test_multimodal_analysis_incompatible_geometry(make_synthetic_raster):
    # Different sizes -> incompatible
    opt_path = make_synthetic_raster("S2A_opt.tif", 200, 200, bands=3)
    sar_path = make_synthetic_raster("S1A_sar.tif", 100, 100, bands=1, tags={'polarization': 'VV'})
    
    opt_id = upload_raster(opt_path)
    sar_id = upload_raster(sar_path)
    
    resp = client.post("/api/v1/multimodal/optical-sar", json={
        "optical_image_id": opt_id,
        "sar_image_id": sar_id,
        "question": "test"
    })
    
    assert resp.status_code == 400
    assert "not aligned" in resp.json()["detail"]
