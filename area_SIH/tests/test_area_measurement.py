import pytest
import numpy as np
from PIL import Image
import os
import tempfile
import cv2

from area_measurement.inference import analyze_area
from area_measurement.preprocessing import load_image
from area_measurement.config import MIN_REGION_AREA_PX


@pytest.fixture
def dummy_rgb_image():
    """Create a dummy RGB image with clear, distinct regions."""
    # Create 520x520 image (same as MODEL_INPUT_SIZE)
    img = np.zeros((520, 520, 3), dtype=np.uint8)
    img[:] = (200, 200, 200)  # Default background

    # 1. Dark Blue "Water" region (should be detected by satellite mode)
    img[50:150, 50:150] = (20, 30, 150)  # BGR format natively for cv2, but PIL uses RGB
    
    # 2. Dark Green "Forest" region
    img[200:400, 200:400] = (10, 80, 20)
    
    # 3. Bright Green/Yellow "Agriculture" region
    img[50:150, 400:500] = (50, 200, 50)
    
    return img


def test_load_image_numpy(dummy_rgb_image):
    """Test loading from a numpy array."""
    data = load_image(dummy_rgb_image)
    assert data.image_rgb.shape == (520, 520, 3)
    assert not data.is_geotiff
    assert data.spatial_resolution is None


def test_load_image_pil(dummy_rgb_image):
    """Test loading from a PIL Image."""
    pil_img = Image.fromarray(dummy_rgb_image)
    data = load_image(pil_img)
    assert data.image_rgb.shape == (520, 520, 3)


def test_satellite_mode_inference(dummy_rgb_image):
    """
    Test the satellite (HSV) segmentation mode.
    Since we know the exact colors of our dummy image, we can predict
    which classes should be found.
    """
    result = analyze_area(dummy_rgb_image, force_satellite_mode=True)
    
    # Check basic structure
    assert "classes" in result
    assert "annotated_image" in result
    assert "class_mask" in result
    assert result["total_pixels"] == 520 * 520
    
    # Check that it found multiple classes
    # (Water, Forest, Agriculture should be found based on the dummy colors)
    classes_found = [c["class_id"] for c in result["classes"]]
    
    # 6 is Water, 4 is Forest
    assert 6 in classes_found
    assert 4 in classes_found
    
    # Check that coverage sums to <= 100%
    assert result["total_coverage_percent"] <= 100.0
    
    # Check that bounding boxes were generated
    for cls in result["classes"]:
        if cls["pixel_area"] >= MIN_REGION_AREA_PX:
            assert len(cls["bounding_boxes"]) > 0
            
            # Check bbox structure
            bbox = cls["bounding_boxes"][0]
            assert "x_min" in bbox
            assert "y_max" in bbox


def test_missing_physical_area():
    """Test that physical area is NOT reported when metadata is absent."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    result = analyze_area(img, force_satellite_mode=True)
    
    assert result["has_physical_area"] is False
    assert result["spatial_resolution_m"] is None
    assert "physical_area_note" in result
    assert result["physical_area_note"] is not None
    
    # Check that classes have None for physical area
    for cls in result["classes"]:
        assert cls.get("area_m2") is None


def test_annotated_image_generation(dummy_rgb_image):
    """Test that the annotated image has the correct dimensions."""
    result = analyze_area(dummy_rgb_image, force_satellite_mode=True)
    annotated = result["annotated_image"]
    
    assert annotated.shape == (520, 520, 3)
    assert annotated.dtype == np.uint8
