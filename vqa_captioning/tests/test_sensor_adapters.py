"""
Tests for Sentinel-2 optical and Sentinel-1 SAR preprocessing adapters.
"""

import numpy as np
import pytest
from PIL import Image

from vqa_captioning.preprocessing.sensor_adapters import Sentinel2Adapter, Sentinel1SARAdapter

def test_sentinel2_rgb_composite_creation():
    # Create 12-band synthetic patch (12, 120, 120)
    fake_s2 = np.random.uniform(200, 3000, (12, 120, 120)).astype(np.float32)
    rgb_img = Sentinel2Adapter.create_rgb_composite(fake_s2)

    assert isinstance(rgb_img, Image.Image)
    assert rgb_img.size == (120, 120)
    assert rgb_img.mode == "RGB"

def test_sentinel2_band_normalization():
    band = np.array([[0.0, 500.0], [2000.0, 10000.0]], dtype=np.float32)
    norm = Sentinel2Adapter.normalize_band(band)
    assert norm.dtype == np.uint8
    assert norm.min() >= 0
    assert norm.max() <= 255

def test_sentinel1_sar_composite_creation():
    # VV and VH channels in dB (-25 to 0 dB)
    vv = np.random.uniform(-20, -5, (120, 120)).astype(np.float32)
    vh = np.random.uniform(-25, -10, (120, 120)).astype(np.float32)

    sar_img = Sentinel1SARAdapter.create_sar_composite(vv, vh)
    assert isinstance(sar_img, Image.Image)
    assert sar_img.size == (120, 120)
    assert sar_img.mode == "RGB"

def test_sentinel1_linear_to_db():
    linear = np.array([0.01, 0.1, 1.0], dtype=np.float32)
    db = Sentinel1SARAdapter.linear_to_db(linear)
    assert np.isclose(db[2], 0.0, atol=1e-3)
    assert np.isclose(db[1], -10.0, atol=1e-3)
    assert np.isclose(db[0], -20.0, atol=1e-3)
