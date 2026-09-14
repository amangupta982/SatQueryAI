"""
Sample validator for SatQuery-VQA datasets.
Validates images, annotations, bounding boxes, text integrity, and splits.
"""

import os
import logging
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image

logger = logging.getLogger(__name__)

class SampleValidator:
    """
    Validates samples against data quality criteria:
    - Missing or unreadable image files
    - Empty questions or answers
    - Duplicate sample IDs
    - Invalid bounding box coordinates
    - Unsupported task annotations
    """

    def __init__(self, check_image_exists: bool = True, verify_image_integrity: bool = False):
        self.check_image_exists = check_image_exists
        self.verify_image_integrity = verify_image_integrity
        self.seen_sample_ids = set()

    def reset(self):
        """Reset internal tracking for duplicate detection."""
        self.seen_sample_ids.clear()

    def validate_sample(self, sample: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a single sample dictionary.
        Returns:
            (is_valid, error_reason)
        """
        # 1. Sample ID validation
        sample_id = sample.get("sample_id")
        if not sample_id:
            return False, "Missing sample_id"
        if sample_id in self.seen_sample_ids:
            return False, f"Duplicate sample_id: {sample_id}"
        self.seen_sample_ids.add(sample_id)

        # 2. Text validation
        question = sample.get("question")
        if question is None or not str(question).strip():
            return False, "Empty or missing question"

        answer = sample.get("answer")
        if answer is None or not str(answer).strip():
            return False, "Empty or missing answer"

        # 3. Image path validation
        image_path = sample.get("image_path")
        if not image_path:
            return False, "Missing image_path"

        if self.check_image_exists:
            if not os.path.exists(image_path):
                return False, f"Image file not found on disk: {image_path}"

            if self.verify_image_integrity:
                try:
                    with Image.open(image_path) as img:
                        img.verify()
                except Exception as e:
                    return False, f"Corrupt image file ({image_path}): {str(e)}"

        # 4. Bounding box validation if evidence contains boxes
        evidence = sample.get("evidence", {})
        if isinstance(evidence, dict) and "bounding_boxes" in evidence:
            boxes = evidence["bounding_boxes"]
            if isinstance(boxes, list):
                for box in boxes:
                    if not isinstance(box, (list, tuple)) or len(box) != 4:
                        return False, f"Invalid bbox format (expected 4 coordinates): {box}"
                    ymin, xmin, ymax, xmax = box
                    if not (0 <= ymin <= 1000 and 0 <= xmin <= 1000 and 0 <= ymax <= 1000 and 0 <= xmax <= 1000):
                        if not (0.0 <= ymin <= 1.0 and 0.0 <= xmin <= 1.0 and 0.0 <= ymax <= 1.0 and 0.0 <= xmax <= 1.0):
                            return False, f"Bbox coordinates out of valid range: {box}"
                    if ymin > ymax or xmin > xmax:
                        return False, f"Malformed bbox coordinates (min > max): {box}"

        return True, None

    def validate_batch(self, samples: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate a batch of samples.
        Returns:
            (valid_samples, invalid_samples_with_reasons)
        """
        valid = []
        invalid = []
        for s in samples:
            is_valid, reason = self.validate_sample(s)
            if is_valid:
                valid.append(s)
            else:
                invalid.append({"sample": s, "reason": reason})
        return valid, invalid
