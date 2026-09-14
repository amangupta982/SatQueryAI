"""
Utility functions for the Area Measurement module.

Provides helper functions for bounding box extraction, label placement,
class information lookup, and formatting.
"""

import numpy as np
from area_measurement.config import LAND_COVER_CLASSES


def get_class_info(class_id: int) -> dict:
    """Get class metadata by ID."""
    return LAND_COVER_CLASSES.get(class_id, LAND_COVER_CLASSES[0])


def get_class_name(class_id: int) -> str:
    """Get human-readable class name."""
    return get_class_info(class_id)["name"]


def get_class_color_bgr(class_id: int) -> tuple:
    """Get BGR color for OpenCV rendering."""
    return get_class_info(class_id)["color_bgr"]


def get_class_color_rgb(class_id: int) -> tuple:
    """Get RGB color for PIL/display."""
    return get_class_info(class_id)["color_rgb"]


def is_displayable_class(class_id: int) -> bool:
    """Check if a class should be displayed in output."""
    return get_class_info(class_id).get("display", False)


def format_pixel_area(pixel_count: int) -> str:
    """Format pixel area with thousands separator."""
    return f"{pixel_count:,}"


def format_percentage(pct: float) -> str:
    """Format percentage to 2 decimal places."""
    return f"{pct:.2f}%"


def format_physical_area(area_m2: float) -> dict:
    """
    Convert area in m² to multiple units.
    
    Returns:
        dict with keys: area_m2, area_hectares, area_km2
    """
    return {
        "area_m2": round(area_m2, 2),
        "area_hectares": round(area_m2 / 10000, 4),
        "area_km2": round(area_m2 / 1_000_000, 6),
    }


def compute_bounding_box(mask: np.ndarray) -> tuple:
    """
    Compute the bounding box of a binary mask.
    
    Args:
        mask: 2D boolean/binary array.
        
    Returns:
        (x_min, y_min, x_max, y_max) or None if mask is empty.
    """
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any() or not cols.any():
        return None
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]
    return (int(x_min), int(y_min), int(x_max), int(y_max))


def find_label_position(bbox: tuple, image_shape: tuple, label_size: tuple) -> tuple:
    """
    Find the best position for a label near a bounding box.
    Tries to place above the box; falls back to inside-top if above is off-screen.
    
    Args:
        bbox: (x_min, y_min, x_max, y_max)
        image_shape: (height, width)
        label_size: (label_width, label_height)
        
    Returns:
        (x, y) position for the label's bottom-left corner.
    """
    x_min, y_min, x_max, y_max = bbox
    h, w = image_shape[:2]
    lw, lh = label_size

    # Try above the bounding box
    label_x = x_min
    label_y = y_min - 5  # 5px gap above box

    # If label goes off top, place inside top of box
    if label_y - lh < 0:
        label_y = y_min + lh + 5

    # If label goes off right, shift left
    if label_x + lw > w:
        label_x = max(0, w - lw)

    return (int(label_x), int(label_y))


def create_summary_table(class_results: list) -> str:
    """
    Create a formatted text summary table of area results.
    
    Args:
        class_results: List of dicts with class area information.
        
    Returns:
        Formatted string table.
    """
    header = f"{'CLASS':<25} {'PIXELS':>12} {'COVERAGE':>10}"
    separator = "-" * 50

    lines = [header, separator]

    for cls in sorted(class_results, key=lambda x: x["coverage_percent"], reverse=True):
        if cls["coverage_percent"] < 0.01:
            continue
        line = (
            f"{cls['class_name']:<25} "
            f"{format_pixel_area(cls['pixel_area']):>12} "
            f"{format_percentage(cls['coverage_percent']):>10}"
        )
        lines.append(line)

        # Add physical area if available
        if "area_m2" in cls and cls["area_m2"] is not None:
            phys = format_physical_area(cls["area_m2"])
            lines.append(
                f"{'':>25} "
                f"{phys['area_m2']:>10.0f} m²  "
                f"{phys['area_hectares']:>8.2f} ha"
            )

    lines.append(separator)
    return "\n".join(lines)
