"""
Visualization for the Area Measurement module.

Creates annotated output images with:
- Semi-transparent colored segmentation masks per class
- Bounding boxes (class-specific colors; Building/Urban = GREEN)
- Labels with class name, pixel area, and coverage percentage
- Smart label placement to avoid overlap
- Legend/summary bar
"""

import numpy as np
import cv2
from area_measurement.config import LAND_COVER_CLASSES, MASK_ALPHA, BBOX_THICKNESS


def create_annotated_image(
    original_image: np.ndarray,
    class_mask: np.ndarray,
    area_results: dict,
) -> np.ndarray:
    """
    Create the final annotated area-measurement image.
    
    Overlays semi-transparent colored masks, bounding boxes, and labels
    on the original image at its original resolution.
    
    Args:
        original_image: (H, W, 3) RGB uint8 original image.
        class_mask: (H, W) integer class mask from segmentation.
        area_results: Dict from calculate_areas().
        
    Returns:
        (H, W, 3) RGB uint8 annotated image.
    """
    # Work in BGR for OpenCV drawing
    img_bgr = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)
    overlay = img_bgr.copy()
    h, w = img_bgr.shape[:2]

    # ── Step 1: Draw semi-transparent masks ──
    for cls_result in area_results["classes"]:
        cls_id = cls_result["class_id"]
        color_bgr = cls_result["color_bgr"]
        cls_binary = (class_mask == cls_id)

        if not cls_binary.any():
            continue

        # Fill mask region with class color
        overlay[cls_binary] = color_bgr

    # Blend overlay with original
    annotated = cv2.addWeighted(overlay, MASK_ALPHA, img_bgr, 1 - MASK_ALPHA, 0)

    # ── Step 2: Draw bounding boxes and labels ──
    used_label_positions = []  # Track label positions to avoid overlap

    for cls_result in area_results["classes"]:
        cls_id = cls_result["class_id"]
        color_bgr = cls_result["color_bgr"]
        class_name = cls_result["class_name"]
        coverage = cls_result["coverage_percent"]
        pixel_area = cls_result["pixel_area"]

        # Draw bounding box for each instance
        for i, bbox_info in enumerate(cls_result["bounding_boxes"]):
            x1 = bbox_info["x_min"]
            y1 = bbox_info["y_min"]
            x2 = bbox_info["x_max"]
            y2 = bbox_info["y_max"]

            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color_bgr, BBOX_THICKNESS)

            # Draw corner markers for emphasis
            corner_len = min(15, (x2 - x1) // 4, (y2 - y1) // 4)
            if corner_len > 3:
                _draw_corners(annotated, x1, y1, x2, y2, color_bgr, corner_len)

        # ── Step 3: Draw label for the class ──
        # Place one label per class (at the largest instance)
        if cls_result["bounding_boxes"]:
            # Find the largest instance for label placement
            largest_bbox = max(
                cls_result["bounding_boxes"],
                key=lambda b: b["instance_pixel_area"],
            )

            label_lines = [
                class_name.upper(),
                f"Area: {pixel_area:,} px",
                f"Coverage: {coverage:.2f}%",
            ]

            # Add physical area if available
            if cls_result.get("area_m2") is not None:
                label_lines.append(f"{cls_result['area_hectares']:.2f} ha")

            _draw_label(
                annotated,
                label_lines,
                largest_bbox["x_min"],
                largest_bbox["y_min"],
                color_bgr,
                used_label_positions,
                (h, w),
            )

    # ── Step 4: Draw legend ──
    annotated = _draw_legend(annotated, area_results)

    # Convert back to RGB
    return cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)


def _draw_corners(img, x1, y1, x2, y2, color, length, thickness=2):
    """Draw corner markers on a bounding box for visual emphasis."""
    # Top-left
    cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
    # Top-right
    cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
    # Bottom-left
    cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
    # Bottom-right
    cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)


def _draw_label(img, lines, x, y, color_bgr, used_positions, img_shape, font_scale=0.45):
    """
    Draw a multi-line label with background near (x, y).
    Adjusts position to avoid overlap with previously placed labels.
    """
    h_img, w_img = img_shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 1
    line_height = 18
    padding = 5

    # Calculate label dimensions
    max_text_w = 0
    for line in lines:
        (tw, _), _ = cv2.getTextSize(line, font, font_scale, thickness)
        max_text_w = max(max_text_w, tw)

    label_w = max_text_w + 2 * padding
    label_h = len(lines) * line_height + 2 * padding

    # Find non-overlapping position
    label_x = x
    label_y = y - label_h - 5  # Try above bbox

    # Adjust if off-screen
    if label_y < 0:
        label_y = y + 5
    if label_x + label_w > w_img:
        label_x = max(0, w_img - label_w)
    if label_y + label_h > h_img:
        label_y = max(0, h_img - label_h)

    # Avoid overlap with existing labels
    attempts = 0
    while _overlaps(label_x, label_y, label_w, label_h, used_positions) and attempts < 10:
        label_y += label_h + 5
        if label_y + label_h > h_img:
            label_y = 5
            label_x += label_w + 10
        attempts += 1

    used_positions.append((label_x, label_y, label_w, label_h))

    # Draw background rectangle
    cv2.rectangle(
        img,
        (label_x, label_y),
        (label_x + label_w, label_y + label_h),
        (0, 0, 0),
        cv2.FILLED,
    )
    cv2.rectangle(
        img,
        (label_x, label_y),
        (label_x + label_w, label_y + label_h),
        color_bgr,
        1,
    )

    # Draw text lines
    for i, line in enumerate(lines):
        text_y = label_y + padding + (i + 1) * line_height - 4
        text_color = color_bgr if i == 0 else (255, 255, 255)
        cv2.putText(
            img, line, (label_x + padding, text_y),
            font, font_scale, text_color, thickness, cv2.LINE_AA,
        )


def _overlaps(x, y, w, h, used):
    """Check if a rectangle overlaps with any previously used positions."""
    for ux, uy, uw, uh in used:
        if not (x + w < ux or x > ux + uw or y + h < uy or y > uy + uh):
            return True
    return False


def _draw_legend(img, area_results):
    """
    Draw a compact legend bar at the bottom of the image.
    Shows all detected classes with their colors and coverage percentages.
    """
    h, w = img.shape[:2]
    classes = area_results["classes"]

    if not classes:
        return img

    # Legend dimensions
    legend_item_h = 22
    legend_padding = 8
    legend_h = len(classes) * legend_item_h + 2 * legend_padding + 25  # +25 for title
    legend_w = min(320, w - 20)

    # Position: bottom-right corner
    lx = w - legend_w - 10
    ly = h - legend_h - 10

    # Ensure within bounds
    if lx < 10:
        lx = 10
    if ly < 10:
        ly = 10

    # Draw semi-transparent background
    sub_img = img[ly:ly + legend_h, lx:lx + legend_w]
    black_bg = np.zeros_like(sub_img)
    blended = cv2.addWeighted(sub_img, 0.3, black_bg, 0.7, 0)
    img[ly:ly + legend_h, lx:lx + legend_w] = blended

    # Draw border
    cv2.rectangle(img, (lx, ly), (lx + legend_w, ly + legend_h), (100, 100, 100), 1)

    # Draw title
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(
        img, "AREA SUMMARY", (lx + legend_padding, ly + 18),
        font, 0.45, (255, 255, 255), 1, cv2.LINE_AA,
    )

    # Draw separator line
    cv2.line(
        img, (lx + 5, ly + 24), (lx + legend_w - 5, ly + 24),
        (100, 100, 100), 1,
    )

    # Draw each class entry
    for i, cls in enumerate(classes):
        entry_y = ly + 30 + i * legend_item_h

        # Color swatch
        swatch_x = lx + legend_padding
        swatch_y = entry_y + 2
        cv2.rectangle(
            img,
            (swatch_x, swatch_y),
            (swatch_x + 12, swatch_y + 12),
            cls["color_bgr"],
            cv2.FILLED,
        )

        # Class name
        cv2.putText(
            img, cls["class_name"],
            (swatch_x + 18, entry_y + 13),
            font, 0.35, (255, 255, 255), 1, cv2.LINE_AA,
        )

        # Coverage percentage
        pct_text = f"{cls['coverage_percent']:.1f}%"
        cv2.putText(
            img, pct_text,
            (lx + legend_w - 60, entry_y + 13),
            font, 0.35, cls["color_bgr"], 1, cv2.LINE_AA,
        )

    # Add physical area note if needed
    if area_results.get("physical_area_note"):
        note_y = ly + legend_h + 15
        if note_y < h - 5:
            cv2.putText(
                img, "* Pixel area only (no geospatial metadata)",
                (lx, note_y), font, 0.3, (150, 150, 150), 1, cv2.LINE_AA,
            )

    return img


def create_summary_image(area_results: dict, width: int = 600) -> np.ndarray:
    """
    Create a standalone summary table image.
    
    This is separate from the annotated image and can be displayed
    alongside it in the UI.
    
    Args:
        area_results: Dict from calculate_areas().
        width: Width of the summary image.
        
    Returns:
        (H, W, 3) BGR uint8 summary table image.
    """
    classes = area_results["classes"]
    has_physical = area_results["has_physical_area"]

    font = cv2.FONT_HERSHEY_SIMPLEX
    row_h = 30
    header_h = 45
    padding = 15

    # Calculate height
    num_rows = len(classes) + 1  # +1 for header
    height = header_h + num_rows * row_h + 2 * padding + 30  # +30 for note

    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = (30, 30, 30)  # Dark background

    # Header
    y = header_h
    cv2.putText(img, "CLASS", (padding, y - 10), font, 0.45, (200, 200, 200), 1)
    cv2.putText(img, "PIXELS", (200, y - 10), font, 0.45, (200, 200, 200), 1)
    cv2.putText(img, "COVERAGE", (320, y - 10), font, 0.45, (200, 200, 200), 1)
    if has_physical:
        cv2.putText(img, "AREA", (450, y - 10), font, 0.45, (200, 200, 200), 1)

    # Separator
    cv2.line(img, (padding, y), (width - padding, y), (80, 80, 80), 1)

    # Data rows
    for i, cls in enumerate(classes):
        row_y = y + (i + 1) * row_h

        # Color swatch + name
        cv2.rectangle(img, (padding, row_y - 12), (padding + 10, row_y - 2), cls["color_bgr"], cv2.FILLED)
        cv2.putText(img, cls["class_name"], (padding + 16, row_y - 2), font, 0.38, (255, 255, 255), 1)

        # Pixel area
        cv2.putText(img, f"{cls['pixel_area']:,}", (200, row_y - 2), font, 0.38, (220, 220, 220), 1)

        # Coverage
        cv2.putText(img, f"{cls['coverage_percent']:.2f}%", (320, row_y - 2), font, 0.38, cls["color_bgr"], 1)

        # Physical area
        if has_physical and cls.get("area_hectares") is not None:
            cv2.putText(img, f"{cls['area_hectares']:.2f} ha", (450, row_y - 2), font, 0.38, (220, 220, 220), 1)

    # Note at bottom
    note_y = y + (len(classes) + 1) * row_h + 10
    if area_results.get("physical_area_note"):
        cv2.putText(img, area_results["physical_area_note"], (padding, note_y), font, 0.3, (150, 150, 150), 1)
    else:
        res = area_results.get("spatial_resolution_m")
        cv2.putText(img, f"Spatial resolution: {res:.1f} m/px", (padding, note_y), font, 0.3, (150, 150, 150), 1)

    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
