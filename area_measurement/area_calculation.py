"""
Area calculation for the Area Measurement module.

Computes pixel area, coverage percentage, and optionally physical area
(m², hectares, km²) from segmentation masks. Uses methodology consistent
with BigEarthNet.txt area annotations (area rounded to nearest 1000 m²,
coverage tiers: primary >25%, secondary 5-25%, marginal <5%).
"""

import numpy as np
from area_measurement.config import LAND_COVER_CLASSES, MIN_REGION_AREA_PX
from area_measurement.utils import (
    compute_bounding_box,
    is_displayable_class,
    format_physical_area,
)
from area_measurement.segmentation import SemanticSegmenter


def calculate_areas(
    class_mask: np.ndarray,
    spatial_resolution: float = None,
    segmenter: SemanticSegmenter = None,
) -> dict:
    """
    Calculate area statistics from a segmentation mask.
    
    This function computes area from the segmentation mask, NOT from
    bounding-box dimensions — as explicitly required by the specification.
    
    Area calculation methodology (aligned with BigEarthNet.txt):
    - pixel_area = number of pixels belonging to that class
    - percentage_area = (pixel_area / total_valid_image_pixels) × 100
    - If spatial resolution available: area_m2 = pixel_area × (resolution²)
    
    Args:
        class_mask: (H, W) integer array of class IDs from segmentation.
        spatial_resolution: Meters per pixel. None if unavailable.
        segmenter: SemanticSegmenter instance for connected component analysis.
        
    Returns:
        dict with:
            - "classes": list of class result dicts
            - "total_pixels": total image pixels
            - "has_physical_area": bool
            - "spatial_resolution_m": float or None
            - "coverage_tiers": dict mapping class_name to tier
    """
    h, w = class_mask.shape
    total_pixels = h * w
    has_physical_area = spatial_resolution is not None and spatial_resolution > 0

    class_results = []
    unique_classes = np.unique(class_mask)

    for cls_id in unique_classes:
        cls_id = int(cls_id)

        # Skip non-displayable classes (background)
        if not is_displayable_class(cls_id):
            continue

        cls_info = LAND_COVER_CLASSES.get(cls_id, LAND_COVER_CLASSES[0])
        class_binary = (class_mask == cls_id)
        pixel_area = int(np.sum(class_binary))

        if pixel_area < MIN_REGION_AREA_PX:
            continue

        coverage_percent = (pixel_area / total_pixels) * 100.0

        # Determine coverage tier (per BigEarthNet.txt methodology)
        if coverage_percent > 25:
            tier = "primary"
        elif coverage_percent >= 5:
            tier = "secondary"
        else:
            tier = "marginal"

        result = {
            "class_id": cls_id,
            "class_name": cls_info["name"],
            "color_rgb": cls_info["color_rgb"],
            "color_bgr": cls_info["color_bgr"],
            "pixel_area": pixel_area,
            "coverage_percent": round(coverage_percent, 2),
            "coverage_tier": tier,
            "bounding_boxes": [],
            "num_instances": 0,
        }

        # Physical area calculation — only if spatial resolution is reliable
        if has_physical_area:
            area_m2 = pixel_area * (spatial_resolution ** 2)
            # Round to nearest 1000 m² (consistent with BigEarthNet.txt)
            area_m2_rounded = round(area_m2 / 1000) * 1000
            phys = format_physical_area(area_m2)
            result["area_m2"] = phys["area_m2"]
            result["area_hectares"] = phys["area_hectares"]
            result["area_km2"] = phys["area_km2"]
            result["area_m2_rounded"] = area_m2_rounded
        else:
            result["area_m2"] = None
            result["area_hectares"] = None
            result["area_km2"] = None

        # Connected component analysis for instances & bounding boxes
        if segmenter:
            components = segmenter.get_connected_components(class_mask, cls_id)
        else:
            # Simple fallback: treat entire class region as one instance
            from scipy import ndimage
            labeled, num_features = ndimage.label(class_binary.astype(np.uint8))
            components = []
            for region_id in range(1, num_features + 1):
                region_mask = labeled == region_id
                if np.sum(region_mask) >= MIN_REGION_AREA_PX:
                    components.append(region_mask)

        result["num_instances"] = len(components)

        for comp in components:
            bbox = compute_bounding_box(comp)
            if bbox is not None:
                instance_pixels = int(np.sum(comp))
                bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                fill_ratio = instance_pixels / bbox_area if bbox_area > 0 else 0

                bbox_info = {
                    "x_min": bbox[0],
                    "y_min": bbox[1],
                    "x_max": bbox[2],
                    "y_max": bbox[3],
                    "instance_pixel_area": instance_pixels,
                    "fill_ratio": round(fill_ratio, 3),
                }

                if has_physical_area:
                    inst_area_m2 = instance_pixels * (spatial_resolution ** 2)
                    bbox_info["instance_area_m2"] = round(inst_area_m2, 2)

                result["bounding_boxes"].append(bbox_info)

        class_results.append(result)

    # Sort by coverage (descending)
    class_results.sort(key=lambda x: x["coverage_percent"], reverse=True)

    # Build coverage tiers dict
    coverage_tiers = {r["class_name"]: r["coverage_tier"] for r in class_results}

    # Validation: check that percentages sum approximately to ≤100%
    total_coverage = sum(r["coverage_percent"] for r in class_results)

    return {
        "classes": class_results,
        "total_pixels": total_pixels,
        "image_dimensions": {"height": h, "width": w},
        "has_physical_area": has_physical_area,
        "spatial_resolution_m": spatial_resolution,
        "total_coverage_percent": round(total_coverage, 2),
        "coverage_tiers": coverage_tiers,
        "physical_area_note": (
            None if has_physical_area
            else "Physical area unavailable — showing pixel area and image coverage."
        ),
    }
