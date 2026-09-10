import pytest
import os
import rasterio
from rasterio.transform import Affine
from fastapi.testclient import TestClient
from app.main import app
import numpy as np

client = TestClient(app)

@pytest.fixture
def make_synthetic_raster(tmp_path):
    def _make_raster(filename, crs, transform, width, height):
        path = tmp_path / filename
        data = np.zeros((height, width), dtype=np.uint8)
        with rasterio.open(
            str(path),
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=data.dtype,
            crs=crs,
            transform=transform,
        ) as dst:
            dst.write(data, 1)
        return str(path)
    return _make_raster

def upload_raster(path):
    with open(path, "rb") as f:
        resp = client.post("/api/v1/images/upload", files={"file": (os.path.basename(path), f, "image/tiff")})
    return resp.json()["image_id"]

def test_aligned_images(make_synthetic_raster):
    transform = Affine.translation(10, 10) * Affine.scale(10, -10)
    img1 = make_synthetic_raster("img1.tif", "+proj=latlong", transform, 100, 100)
    img2 = make_synthetic_raster("img2.tif", "+proj=latlong", transform, 100, 100)
    
    id1, id2 = upload_raster(img1), upload_raster(img2)
    resp = client.post("/api/v1/images/compare", json={"image_id_1": id1, "image_id_2": id2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["state"] == "ALIGNED"
    assert data["overlap_percentage_1"] == 100.0
    assert data["identical_crs"] is True

def test_overlapping_different_resolution(make_synthetic_raster):
    transform1 = Affine.translation(10, 10) * Affine.scale(10, -10)
    transform2 = Affine.translation(10, 10) * Affine.scale(20, -20)
    # img1 is 100x100 at 10m (1000m x 1000m)
    # img2 is 50x50 at 20m (1000m x 1000m)
    img1 = make_synthetic_raster("img1.tif", "+proj=latlong", transform1, 100, 100)
    img2 = make_synthetic_raster("img2.tif", "+proj=latlong", transform2, 50, 50)
    
    id1, id2 = upload_raster(img1), upload_raster(img2)
    resp = client.post("/api/v1/images/compare", json={"image_id_1": id1, "image_id_2": id2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["state"] == "REQUIRES_REGISTRATION"
    assert data["identical_transform"] is False
    assert data["identical_dimensions"] is False
    assert data["resolution_match"] is False

def test_incompatible_no_overlap(make_synthetic_raster):
    # Completely disjoint
    transform1 = Affine.translation(10, 10) * Affine.scale(10, -10)
    transform2 = Affine.translation(2000, 2000) * Affine.scale(10, -10)
    img1 = make_synthetic_raster("img1.tif", "+proj=latlong", transform1, 100, 100)
    img2 = make_synthetic_raster("img2.tif", "+proj=latlong", transform2, 100, 100)
    
    id1, id2 = upload_raster(img1), upload_raster(img2)
    resp = client.post("/api/v1/images/compare", json={"image_id_1": id1, "image_id_2": id2})
    assert resp.status_code == 200
    assert resp.json()["state"] == "INCOMPATIBLE"

def test_different_crs_overlapping(make_synthetic_raster):
    # Same geographic area roughly, but different CRS
    transform1 = Affine.translation(10.0, 10.0) * Affine.scale(1.0, -1.0)
    # Using NAD83 (EPSG:4269) which will overlap heavily with WGS84
    img1 = make_synthetic_raster("img1.tif", "EPSG:4269", transform1, 100, 100)
    # WGS 84 (EPSG:4326)
    img2 = make_synthetic_raster("img2.tif", "EPSG:4326", transform1, 100, 100)
    
    id1, id2 = upload_raster(img1), upload_raster(img2)
    resp = client.post("/api/v1/images/compare", json={"image_id_1": id1, "image_id_2": id2})
    assert resp.status_code == 200
    data = resp.json()
    # It will overlap, but different CRS
    assert data["state"] == "REQUIRES_REGISTRATION"
    assert data["identical_crs"] is False
