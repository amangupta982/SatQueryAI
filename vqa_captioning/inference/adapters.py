"""
Evidence adapters for Counting and Land-Cover Area questions.
Enforces quantitative integrity and provides clean routing hooks to external
object detection (grounding_change) and raster segmentation modules.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple, List
import numpy as np

logger = logging.getLogger(__name__)

class CountEvidenceAdapter:
    """
    Handles counting queries with strict distinction between:
    1. Land-cover patch / contiguous region counting (supported by BigEarthNet.txt).
    2. Discrete physical object counting (e.g. individual buildings, vehicles).
    """

    OBJECT_COUNT_PATTERNS = [
        r"how many (?:buildings|houses|structures|homes)",
        r"how many (?:cars|vehicles|trucks|boats|ships|planes|aircraft)",
        r"count (?:all )?(?:the )?(?:buildings|vehicles|ships|structures)",
    ]

    PATCH_COUNT_PATTERNS = [
        r"how many (?:distinct )?(?:regions|patches|zones|areas|forests|water bodies)",
        r"count (?:the )?(?:patches|regions)",
    ]

    def __init__(self, external_detector_fn: Optional[Any] = None):
        """
        Args:
            external_detector_fn: Optional callable hook into grounding_change module
                                  (e.g. GroundingDINO on high-resolution imagery).
        """
        self.external_detector_fn = external_detector_fn

    def is_object_level_count(self, question: str) -> bool:
        """Determines if question asks for discrete physical objects."""
        q_low = question.lower()
        for pat in self.OBJECT_COUNT_PATTERNS:
            if re.search(pat, q_low):
                return True
        return False

    def handle_count_query(
        self,
        image_input: Any,
        question: str,
        vqa_model_fn: Any,
    ) -> Dict[str, Any]:
        """
        Routes count queries based on query type:
        - If discrete object count and external detector is available: delegate to detector.
        - If discrete object count and no detector: explain dataset limitation and decline hallucination.
        - If land-cover region count: query SatQuery-VQA model directly.
        """
        if self.is_object_level_count(question):
            if self.external_detector_fn is not None:
                logger.info("Routing discrete object count query to grounding_change detector.")
                return self.external_detector_fn(image_input, question)
            else:
                return {
                    "answer": (
                        "BigEarthNet.txt satellite imagery (10m–20m resolution) does not provide "
                        "individual building or vehicle instance annotations. Exact object counting requires "
                        "high-resolution imagery and the object detection module (grounding_change)."
                    ),
                    "confidence": None,
                    "task": "count",
                    "evidence": {
                        "limitation": "Discrete object counting not supported on 10m CLC resolution without object detection head.",
                        "recommended_module": "grounding_change",
                    },
                    "model": "SatQuery-VQA (CountEvidenceAdapter)",
                }

        # Otherwise, standard land-cover patch count
        return vqa_model_fn(image_input, question, task="count")


class AreaCalculator:
    """Calculates true ground area from raster segmentation masks or GSD."""

    @staticmethod
    def calculate_mask_area(
        binary_mask: np.ndarray,
        gsd_meters: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Computes exact ground area from a binary segmentation mask:
        Area = pixel_count * (gsd ** 2)
        """
        pixel_count = int(np.sum(binary_mask > 0))
        total_pixels = int(binary_mask.size)
        area_m2 = pixel_count * (gsd_meters ** 2)
        area_km2 = area_m2 / 1_000_000.0
        percentage = (pixel_count / total_pixels) * 100.0 if total_pixels > 0 else 0.0

        return {
            "pixel_count": pixel_count,
            "total_pixels": total_pixels,
            "percentage": round(percentage, 2),
            "area_m2": round(area_m2, 1),
            "area_km2": round(area_km2, 4),
            "gsd_meters": gsd_meters,
        }


class LandCoverEvidenceAdapter:
    """
    Adapts land-cover area and coverage questions.
    Distinguishes between categorical coverage tiers (>25%, 5-25%, <5%) and exact pixel calculation.
    """

    def __init__(self, raster_analyzer_fn: Optional[Any] = None):
        self.raster_analyzer_fn = raster_analyzer_fn
        self.area_calc = AreaCalculator()

    def handle_area_query(
        self,
        image_input: Any,
        question: str,
        vqa_model_fn: Any,
        segmentation_mask: Optional[np.ndarray] = None,
        gsd_meters: float = 10.0,
    ) -> Dict[str, Any]:
        """
        If a segmentation mask is provided, computes exact raster area.
        Otherwise, uses SatQuery-VQA for categorical dominance and coverage tier.
        """
        if segmentation_mask is not None:
            mask_stats = self.area_calc.calculate_mask_area(segmentation_mask, gsd_meters=gsd_meters)
            return {
                "answer": f"The class covers approximately {mask_stats['percentage']}% of the image ({mask_stats['area_km2']} km²).",
                "confidence": 1.0,
                "task": "area",
                "evidence": {
                    "exact_pixel_metrics": mask_stats,
                    "calculation_method": "raster_pixel_count",
                },
                "model": "SatQuery-RasterEvidenceAdapter",
            }

        # Query VQA model for calibrated relative coverage tier
        res = vqa_model_fn(image_input, question, task="size")
        return res
