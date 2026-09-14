"""
Grounding Engine for Exhaustive Whole-Image Object Detection.

Implements a tiled + whole-image inference pipeline using Grounding DINO
(IDEA-Research/grounding-dino-tiny) for open-vocabulary, multi-instance
detection on satellite/remote-sensing imagery.

Pipeline:
    1. Parse natural-language query → extract visual target label
    2. Whole-image inference pass
    3. Tiled inference with overlapping crops (640×640, 30% overlap)
    4. Coordinate remapping (tile-local → original image)
    5. Merge all candidate detections
    6. NMS deduplication (IoU=0.5)
    7. Giant-box filter (reject boxes > 60% of image area)
    8. Confidence filtering (user threshold)
    9. Sort by confidence descending

Model:
    - Name: Grounding DINO Tiny
    - Checkpoint: IDEA-Research/grounding-dino-tiny
    - Training domain: COCO + O365 + GoldG (general domain, NOT satellite-specific)
    - Limitation: Not trained on remote-sensing imagery; small satellite objects
      may have lower recall compared to domain-specific models.
    - Confidence thresholds: Configurable via box_threshold parameter
"""

import re
import time
import math
import torch
import numpy as np
from PIL import Image
from transformers import pipeline as hf_pipeline


# ─── Query Parsing ──────────────────────────────────────────────────

# Patterns to strip from natural-language queries to extract the visual target
_PREAMBLE_PATTERNS = [
    r"^where\s+(are|is)\s+(the\s+)?",
    r"^how\s+many\s+",
    r"^show\s+(me\s+)?(all\s+)?(the\s+)?",
    r"^find\s+(all\s+)?(the\s+)?",
    r"^locate\s+(all\s+)?(the\s+)?",
    r"^detect\s+(all\s+)?(the\s+)?",
    r"^identify\s+(all\s+)?(the\s+)?",
    r"^what\s+(are|is)\s+(the\s+)?",
    r"^can\s+you\s+(find|show|detect|locate)\s+(me\s+)?(all\s+)?(the\s+)?",
    r"^are\s+there\s+(any\s+)?",
    r"^is\s+there\s+(a\s+|an\s+)?",
]

# Suffixes to strip
_SUFFIX_PATTERNS = [
    r"\s+(in\s+this\s+image|in\s+the\s+image|visible|present|here)\s*[?.!]*$",
    r"\s*[?.!]+$",
]


def parse_query(query: str) -> list[str]:
    """
    Extract visual target label(s) from a natural-language query.

    Handles:
        - "Where are the buildings?" → ["building"]
        - "How many bridges are visible?" → ["bridge"]
        - "Show me all water bodies" → ["water body"]
        - "building, road, water" → ["building", "road", "water"]
        - "buildings" → ["building"]

    Returns:
        list[str]: One or more clean target labels (singular form preferred).
    """
    text = query.strip()

    # If comma-separated, treat as multiple explicit targets
    if "," in text:
        targets = []
        for part in text.split(","):
            part = part.strip().rstrip("?.! ")
            if part:
                targets.append(_singularize(part.lower()))
        return targets if targets else [text.lower()]

    # Strip preamble patterns
    cleaned = text.lower()
    for pattern in _PREAMBLE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()

    # Strip suffix patterns
    for pattern in _SUFFIX_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()

    # Final cleanup
    cleaned = cleaned.strip("?.! ").strip()

    if not cleaned:
        cleaned = text.lower().rstrip("?.! ")

    return [_singularize(cleaned)]


def _singularize(word: str) -> str:
    """Very basic plurals → singular conversion for common RS terms."""
    # Don't singularize short words or specific terms
    if len(word) <= 3:
        return word
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"  # bodies → body, factories → factory
    if word.endswith("ses") or word.endswith("xes") or word.endswith("zes"):
        return word[:-2]  # buses → bus
    if word.endswith("ches") or word.endswith("shes"):
        return word[:-2]  # bridges stays, patches → patch
    if word.endswith("ges") and not word.endswith("dges"):
        return word[:-1]  # Not bridges
    if word.endswith("s") and not word.endswith("ss") and not word.endswith("us"):
        return word[:-1]  # buildings → building, roads → road
    return word


# ─── NMS ────────────────────────────────────────────────────────────

def _compute_iou(box_a: dict, box_b: dict) -> float:
    """Compute IoU between two boxes in {xmin, ymin, xmax, ymax} format."""
    x1 = max(box_a["xmin"], box_b["xmin"])
    y1 = max(box_a["ymin"], box_b["ymin"])
    x2 = min(box_a["xmax"], box_b["xmax"])
    y2 = min(box_a["ymax"], box_b["ymax"])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    if intersection == 0:
        return 0.0

    area_a = (box_a["xmax"] - box_a["xmin"]) * (box_a["ymax"] - box_a["ymin"])
    area_b = (box_b["xmax"] - box_b["xmin"]) * (box_b["ymax"] - box_b["ymin"])
    union = area_a + area_b - intersection

    return intersection / union if union > 0 else 0.0


def nms(detections: list, iou_threshold: float = 0.5) -> list:
    """
    Non-Maximum Suppression.

    Args:
        detections: List of detection dicts with 'score' and 'box' keys.
        iou_threshold: IoU threshold above which the lower-confidence
                       detection is suppressed.

    Returns:
        Filtered list of detections.
    """
    if not detections:
        return []

    # Sort by score descending
    sorted_dets = sorted(detections, key=lambda d: d["score"], reverse=True)
    keep = []

    while sorted_dets:
        best = sorted_dets.pop(0)
        keep.append(best)

        remaining = []
        for det in sorted_dets:
            if _compute_iou(best["box"], det["box"]) < iou_threshold:
                remaining.append(det)
        sorted_dets = remaining

    return keep


# ─── Tiling ─────────────────────────────────────────────────────────

def _generate_tiles(img_w: int, img_h: int,
                    tile_size: int = 640,
                    overlap: float = 0.30) -> list[tuple[int, int, int, int]]:
    """
    Generate overlapping tile coordinates that cover the entire image.

    Returns:
        List of (x_start, y_start, x_end, y_end) tuples.
    """
    stride = int(tile_size * (1.0 - overlap))
    tiles = []

    y = 0
    while y < img_h:
        y_end = min(y + tile_size, img_h)
        # If the remaining strip is too small, extend back
        if y_end - y < tile_size // 3 and y > 0:
            y = max(0, img_h - tile_size)
            y_end = img_h

        x = 0
        while x < img_w:
            x_end = min(x + tile_size, img_w)
            if x_end - x < tile_size // 3 and x > 0:
                x = max(0, img_w - tile_size)
                x_end = img_w

            tiles.append((x, y, x_end, y_end))

            if x_end >= img_w:
                break
            x += stride

        if y_end >= img_h:
            break
        y += stride

    # Deduplicate (can happen at edges)
    seen = set()
    unique_tiles = []
    for t in tiles:
        if t not in seen:
            seen.add(t)
            unique_tiles.append(t)

    return unique_tiles


# ─── Grounding Engine ───────────────────────────────────────────────

class GroundingEngine:
    """
    Exhaustive whole-image grounding engine.

    Uses Grounding DINO Tiny via HuggingFace zero-shot-object-detection
    pipeline with tiled inference for comprehensive satellite image analysis.
    """

    _instance = None

    # ── Configuration ──
    MODEL_ID = "IDEA-Research/grounding-dino-tiny"
    TILE_SIZE = 640
    TILE_OVERLAP = 0.30
    NMS_IOU_THRESHOLD = 0.50
    GIANT_BOX_RATIO = 0.60       # Reject boxes > 60% of image area
    MIN_BOX_PIXELS = 100         # Reject boxes smaller than 10×10
    INTERNAL_THRESHOLD = 0.08    # Very low threshold for maximum recall
    TILING_TRIGGER_PX = 800      # Use tiling when image > 800px on either axis

    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        device_name = "GPU" if self.device == 0 else "CPU"
        print(f"[GroundingEngine] Loading '{self.MODEL_ID}' on {device_name}...")

        self.pipe = hf_pipeline(
            "zero-shot-object-detection",
            model=self.MODEL_ID,
            device=self.device,
        )
        print("[GroundingEngine] Model loaded successfully.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GroundingEngine()
        return cls._instance

    # ── Main predict method ─────────────────────────────────────────

    def predict(
        self,
        image: Image.Image,
        query: str,
        box_threshold: float = 0.20,
        text_threshold: float = 0.20,
    ) -> dict:
        """
        Run exhaustive whole-image grounding.

        Args:
            image: PIL Image (RGB).
            query: Natural-language query string.
            box_threshold: User-facing confidence threshold for final filtering.
            text_threshold: Not used directly by HF pipeline but kept for API compat.

        Returns:
            dict with keys:
                - detections: list of detection dicts
                - target_label: parsed visual target string
                - count: number of final detections
                - processing_time: float seconds
                - pipeline_info: dict with model/tile/threshold details
        """
        start_time = time.time()

        img_w, img_h = image.size
        img_area = img_w * img_h

        # 1. Parse query
        targets = parse_query(query)
        target_label = ", ".join(targets)

        # Format for Grounding DINO (period-terminated)
        candidate_labels = []
        for t in targets:
            formatted = t if t.endswith(".") else t + "."
            if formatted not in candidate_labels:
                candidate_labels.append(formatted)

        print(f"[GroundingEngine] Query: '{query}' -> targets: {targets}")
        print(f"[GroundingEngine] Image: {img_w}x{img_h} = {img_area:,} pixels")

        all_detections = []
        tile_count = 0

        # 2. Whole-image pass
        try:
            whole_dets = self._run_inference(image, candidate_labels)
            all_detections.extend(whole_dets)
            print(f"[GroundingEngine] Whole-image: {len(whole_dets)} raw detections")
        except Exception as e:
            print(f"[GroundingEngine] Whole-image inference error: {e}")

        # 3. Tiled inference (if image is large enough)
        use_tiling = (img_w > self.TILING_TRIGGER_PX or
                      img_h > self.TILING_TRIGGER_PX)

        if use_tiling:
            tiles = _generate_tiles(img_w, img_h,
                                    tile_size=self.TILE_SIZE,
                                    overlap=self.TILE_OVERLAP)
            tile_count = len(tiles)
            print(f"[GroundingEngine] Tiling: {tile_count} tiles "
                  f"({self.TILE_SIZE}px, {self.TILE_OVERLAP:.0%} overlap)")

            for idx, (tx, ty, tx2, ty2) in enumerate(tiles):
                try:
                    crop = image.crop((tx, ty, tx2, ty2))
                    tile_dets = self._run_inference(crop, candidate_labels)

                    # Remap coordinates from tile-local → original image
                    for det in tile_dets:
                        det["box"]["xmin"] += tx
                        det["box"]["ymin"] += ty
                        det["box"]["xmax"] += tx
                        det["box"]["ymax"] += ty

                    all_detections.extend(tile_dets)
                except Exception as e:
                    print(f"[GroundingEngine] Tile {idx+1}/{tile_count} error: {e}")

            print(f"[GroundingEngine] Total raw candidates after tiling: "
                  f"{len(all_detections)}")

        # 4. NMS deduplication
        before_nms = len(all_detections)
        all_detections = nms(all_detections, iou_threshold=self.NMS_IOU_THRESHOLD)
        print(f"[GroundingEngine] After NMS: {len(all_detections)} "
              f"(removed {before_nms - len(all_detections)} duplicates)")

        # 5. Giant-box filter
        filtered = []
        for det in all_detections:
            box = det["box"]
            box_area = (box["xmax"] - box["xmin"]) * (box["ymax"] - box["ymin"])
            if box_area > img_area * self.GIANT_BOX_RATIO:
                continue  # Skip giant boxes
            if box_area < self.MIN_BOX_PIXELS:
                continue  # Skip tiny noise
            filtered.append(det)

        giant_removed = len(all_detections) - len(filtered)
        if giant_removed > 0:
            print(f"[GroundingEngine] Removed {giant_removed} giant/tiny boxes")
        all_detections = filtered

        # 6. Confidence filtering
        final = [d for d in all_detections if d["score"] >= box_threshold]

        # Auto-fallback if strict threshold yields nothing
        if not final and all_detections:
            fallback_thresh = max(0.10, box_threshold * 0.5)
            final = [d for d in all_detections if d["score"] >= fallback_thresh]
            if final:
                print(f"[GroundingEngine] Auto-fallback to threshold "
                      f"{fallback_thresh:.2f}: {len(final)} detections")

        # 7. Sort by confidence descending
        final.sort(key=lambda d: d["score"], reverse=True)

        # Clean labels (remove trailing periods)
        for det in final:
            det["label"] = det["label"].rstrip(".")

        processing_time = time.time() - start_time

        print(f"[GroundingEngine] Final: {len(final)} detections in "
              f"{processing_time:.1f}s")

        return {
            "detections": final,
            "target_label": target_label,
            "count": len(final),
            "processing_time": processing_time,
            "pipeline_info": {
                "model": self.MODEL_ID,
                "tile_count": tile_count,
                "tile_size": self.TILE_SIZE,
                "tile_overlap": self.TILE_OVERLAP,
                "nms_iou_threshold": self.NMS_IOU_THRESHOLD,
                "box_threshold": box_threshold,
                "internal_threshold": self.INTERNAL_THRESHOLD,
                "image_size": f"{img_w}×{img_h}",
                "tiling_used": use_tiling,
            }
        }

    # ── Single-pass inference helper ────────────────────────────────

    def _run_inference(self, image: Image.Image,
                       candidate_labels: list[str]) -> list[dict]:
        """
        Run Grounding DINO on a single image (or crop).

        Returns list of detections with integer box coordinates.
        """
        results = self.pipe(
            image,
            candidate_labels=candidate_labels,
            threshold=self.INTERNAL_THRESHOLD,
        )

        detections = []
        for r in results:
            box = r["box"]
            detections.append({
                "score": float(r["score"]),
                "label": str(r["label"]),
                "box": {
                    "xmin": int(round(box["xmin"])),
                    "ymin": int(round(box["ymin"])),
                    "xmax": int(round(box["xmax"])),
                    "ymax": int(round(box["ymax"])),
                }
            })

        return detections


# ─── Backward compatibility alias ──────────────────────────────────
# So that any old import `from grounding.inference import GroundingModel`
# still works (e.g. tests)
GroundingModel = GroundingEngine
