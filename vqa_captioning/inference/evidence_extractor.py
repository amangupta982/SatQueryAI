"""
Evidence extractor for SatQuery-VQA inference.
Extracts grounded bounding boxes, coverage tiers, and spatial evidence from responses.
"""

import re
from typing import Dict, Any, List, Optional

class EvidenceExtractor:
    """Extracts and validates structured evidence from model generations."""

    @staticmethod
    def extract_bounding_boxes(text: str) -> List[List[float]]:
        """
        Parses normalized bounding boxes [ymin, xmin, ymax, xmax] from text.
        Supports standard JSON-like lists and Qwen coordinate representations.
        """
        boxes = []
        # Pattern 1: [y1, x1, y2, x2]
        matches = re.findall(
            r"\[\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\]",
            text,
        )
        for m in matches:
            try:
                coords = [float(x) for x in m]
                # If coords are scaled [0, 1000], normalize to [0, 1]
                if any(c > 1.0 for c in coords):
                    coords = [round(c / 1000.0, 4) for c in coords]
                ymin, xmin, ymax, xmax = coords
                if 0.0 <= ymin <= 1.0 and 0.0 <= xmin <= 1.0 and ymin < ymax and xmin < xmax:
                    boxes.append([ymin, xmin, ymax, xmax])
            except ValueError:
                continue

        # Pattern 2: <box> y1 x1 y2 x2 </box>
        box_tags = re.findall(r"<box>\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*</box>", text)
        for m in box_tags:
            try:
                coords = [round(float(x) / 1000.0, 4) for x in m]
                ymin, xmin, ymax, xmax = coords
                if 0.0 <= ymin <= 1.0 and 0.0 <= xmin <= 1.0 and ymin < ymax and xmin < xmax:
                    boxes.append([ymin, xmin, ymax, xmax])
            except ValueError:
                continue

        return boxes

    @staticmethod
    def extract_coverage_tier(text: str) -> Optional[str]:
        """Identifies BigEarthNet coverage tier if mentioned."""
        t_low = text.lower()
        if "primary" in t_low or ">25%" in t_low or "> 25%" in t_low:
            return "Primary (>25% image coverage)"
        elif "secondary" in t_low or "5-25%" in t_low or "5% - 25%" in t_low:
            return "Secondary (5-25% image coverage)"
        elif "marginal" in t_low or "<5%" in t_low or "< 5%" in t_low:
            return "Marginal (<5% image coverage)"
        return None

    @classmethod
    def compile_evidence(
        cls,
        raw_answer: str,
        task: str,
        sensor_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Compiles clean evidence dictionary for user response."""
        evidence: Dict[str, Any] = {}
        if sensor_metadata:
            evidence.update(sensor_metadata)

        boxes = cls.extract_bounding_boxes(raw_answer)
        if boxes:
            evidence["bounding_boxes"] = boxes

        tier = cls.extract_coverage_tier(raw_answer)
        if tier:
            evidence["coverage_tier"] = tier

        # Area mentions
        area_match = re.search(r"(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:m2|m²|km2|km²|hectares)", raw_answer, re.IGNORECASE)
        if area_match:
            evidence["mentioned_area"] = area_match.group(0)

        return evidence
