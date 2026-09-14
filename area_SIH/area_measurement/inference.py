"""
Main inference API for the Area Measurement module.

Provides the single entry-point function `analyze_area()` that orchestrates
the full pipeline:

    INPUT IMAGE
         ↓
    Image preprocessing
         ↓
    Land-cover / semantic segmentation
         ↓
    Class masks
         ↓
    Connected-component / region extraction
         ↓
    Area calculation
         ↓
    Bounding boxes + masks
         ↓
    Annotated output image
         ↓
    Area summary

This function is designed to be called by the main Agentic pipeline as:
    "Tool 5 → Area Measurement"
"""

import numpy as np
from PIL import Image
import time

from area_measurement.preprocessing import load_image, ImageData
from area_measurement.segmentation import SemanticSegmenter
from area_measurement.area_calculation import calculate_areas
from area_measurement.visualization import create_annotated_image, create_summary_image
from area_measurement.utils import create_summary_table


# Module-level segmenter instance (lazy-loaded)
_segmenter = None


def _get_segmenter() -> SemanticSegmenter:
    """Get or create the segmenter singleton."""
    global _segmenter
    if _segmenter is None:
        _segmenter = SemanticSegmenter()
    return _segmenter


def analyze_area(source, force_satellite_mode: bool = False) -> dict:
    """
    Main API function: analyze land-cover area of an image.
    
    This is the single clean entry-point for the Area Measurement module.
    It accepts an image (path, PIL Image, or numpy array) and returns
    a complete area analysis result.
    
    Args:
        source: Image source. Can be:
            - str: File path (supports PNG, JPEG, TIFF, GeoTIFF)
            - PIL.Image: Already-loaded image
            - np.ndarray: (H, W, 3) RGB uint8 array
        force_satellite_mode: If True, skip DeepLabV3 and use satellite-
                              optimized HSV color-space segmentation directly.
    
    Returns:
        dict with the following structure:
        {
            "annotated_image": np.ndarray,  # (H, W, 3) RGB uint8
            "summary_image": np.ndarray,    # (H, W, 3) RGB uint8 table
            "class_mask": np.ndarray,       # (H, W) int32 class IDs
            "classes": [
                {
                    "class_id": int,
                    "class_name": str,
                    "color_rgb": tuple,
                    "pixel_area": int,
                    "coverage_percent": float,
                    "coverage_tier": str,       # "primary"/"secondary"/"marginal"
                    "num_instances": int,
                    "bounding_boxes": [...],
                    "area_m2": float or None,
                    "area_hectares": float or None,
                    "area_km2": float or None,
                }
            ],
            "total_pixels": int,
            "image_dimensions": {"height": int, "width": int},
            "has_physical_area": bool,
            "spatial_resolution_m": float or None,
            "total_coverage_percent": float,
            "physical_area_note": str or None,
            "summary_text": str,
            "processing_time_seconds": float,
            "model_used": str,
        }
    
    Example:
        >>> from area_measurement import analyze_area
        >>> result = analyze_area("satellite_image.tif")
        >>> print(result["summary_text"])
        >>> annotated = result["annotated_image"]
    """
    start_time = time.time()

    # ── Step 1: Load and preprocess image ──
    print("[Area Measurement] Step 1/5: Loading image...")
    image_data = load_image(source)
    image_rgb = image_data.image_rgb

    # Determine if satellite mode should be used
    use_satellite = force_satellite_mode or image_data.is_geotiff

    # ── Step 2: Semantic segmentation ──
    print("[Area Measurement] Step 2/5: Running segmentation...")
    segmenter = _get_segmenter()
    class_mask = segmenter.segment(image_rgb, use_satellite_mode=use_satellite)

    model_used = (
        "HSV Color-Space Analysis (satellite-optimized)"
        if use_satellite
        else "DeepLabV3-ResNet101 (torchvision, COCO/VOC pretrained)"
    )

    # ── Step 3: Calculate areas ──
    print("[Area Measurement] Step 3/5: Calculating areas...")
    area_results = calculate_areas(
        class_mask,
        spatial_resolution=image_data.spatial_resolution,
        segmenter=segmenter,
    )

    # ── Step 4: Create annotated image ──
    print("[Area Measurement] Step 4/5: Creating annotated visualization...")
    annotated_image = create_annotated_image(image_rgb, class_mask, area_results)

    # ── Step 5: Create summary ──
    print("[Area Measurement] Step 5/5: Generating summary...")
    summary_image = create_summary_image(area_results)
    summary_text = create_summary_table(area_results["classes"])

    processing_time = time.time() - start_time

    print(f"[Area Measurement] Done. Processed in {processing_time:.2f}s")
    print(f"[Area Measurement] Found {len(area_results['classes'])} land-cover classes.")

    # ── Build result dict ──
    result = {
        "annotated_image": annotated_image,
        "summary_image": summary_image,
        "class_mask": class_mask,
        "classes": area_results["classes"],
        "total_pixels": area_results["total_pixels"],
        "image_dimensions": area_results["image_dimensions"],
        "has_physical_area": area_results["has_physical_area"],
        "spatial_resolution_m": area_results["spatial_resolution_m"],
        "total_coverage_percent": area_results["total_coverage_percent"],
        "coverage_tiers": area_results["coverage_tiers"],
        "physical_area_note": area_results["physical_area_note"],
        "summary_text": summary_text,
        "processing_time_seconds": round(processing_time, 2),
        "model_used": model_used,
    }

    return result


def analyze_area_from_bytes(image_bytes: bytes, filename: str = "image.png", **kwargs) -> dict:
    """
    Convenience function for web API usage.
    Accepts raw image bytes (e.g., from a file upload) and runs analysis.
    
    Args:
        image_bytes: Raw bytes of the image file.
        filename: Original filename (used for format detection).
        **kwargs: Additional arguments passed to analyze_area().
        
    Returns:
        Same result dict as analyze_area().
    """
    import io
    img = Image.open(io.BytesIO(image_bytes))
    return analyze_area(img, **kwargs)
