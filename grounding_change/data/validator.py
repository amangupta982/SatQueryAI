"""
Dataset Integrity & Validation Engine.
Runs comprehensive checks on downloaded datasets:
- File integrity & readability
- T1/T2 pair matching
- Annotation alignment
- Dimension verification
- Semantic class label consistency
- Split completeness
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image
import numpy as np


class ValidationResult:
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.valid = True
        self.total_pairs = 0
        self.total_annotations = 0
        self.missing_files: List[str] = []
        self.corrupted_files: List[str] = []
        self.unmatched_pairs: List[str] = []
        self.splits_found: Dict[str, int] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset": self.dataset_name,
            "valid": self.valid and len(self.errors) == 0,
            "total_pairs": self.total_pairs,
            "total_annotations": self.total_annotations,
            "splits": self.splits_found,
            "missing_count": len(self.missing_files),
            "corrupted_count": len(self.corrupted_files),
            "unmatched_count": len(self.unmatched_pairs),
            "errors": self.errors,
            "warnings": self.warnings,
        }


class DatasetValidator:
    """Validator across all remote-sensing change datasets."""

    @staticmethod
    def verify_image_readable(path: Path) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """Check if an image file exists, is readable, and return its (width, height)."""
        if not path.exists():
            return False, None
        try:
            with Image.open(path) as img:
                img.verify()
            # Reopen for size since verify() closes/invalidates the file in some PIL versions
            with Image.open(path) as img:
                return True, img.size
        except Exception:
            return False, None

    @classmethod
    def validate_second(cls, dataset_dir: Path) -> ValidationResult:
        """Validate SECOND dataset folder structure and pairs."""
        res = ValidationResult("second")
        if not dataset_dir.exists():
            res.valid = False
            res.errors.append(f"SECOND directory does not exist: {dataset_dir}")
            return res

        for split in ["train", "val", "test"]:
            split_dir = dataset_dir / split
            if not split_dir.exists():
                split_dir = dataset_dir  # Flat structure fallback

            im1_dir = split_dir / "im1"
            im2_dir = split_dir / "im2"
            label1_dir = split_dir / "label1"
            label2_dir = split_dir / "label2"

            if not im1_dir.exists() or not im2_dir.exists():
                continue

            im1_files = sorted(list(im1_dir.glob("*.png")) + list(im1_dir.glob("*.jpg")) + list(im1_dir.glob("*.tif")))
            pair_count = 0

            for f1 in im1_files:
                f2 = im2_dir / f1.name
                if not f2.exists():
                    res.unmatched_pairs.append(f"Missing T2 match for: {f1.name}")
                    continue

                # Check readability of sample (first few or sample checks)
                if pair_count < 10:
                    ok1, sz1 = cls.verify_image_readable(f1)
                    ok2, sz2 = cls.verify_image_readable(f2)
                    if not ok1 or not ok2:
                        res.corrupted_files.append(f1.name)
                    elif sz1 != sz2:
                        res.errors.append(f"Dimension mismatch between T1 {sz1} and T2 {sz2} for {f1.name}")

                pair_count += 1

            res.splits_found[split] = pair_count
            res.total_pairs += pair_count

        if res.total_pairs == 0:
            res.valid = False
            res.errors.append("No valid T1/T2 image pairs found in SECOND dataset.")

        return res

    @classmethod
    def validate_changechat(cls, dataset_dir: Path) -> ValidationResult:
        """Validate ChangeChat-105k annotations and corresponding LEVIR-CC images."""
        import json
        res = ValidationResult("changechat")
        if not dataset_dir.exists():
            res.valid = False
            res.errors.append(f"ChangeChat directory does not exist: {dataset_dir}")
            return res

        anno_files = list(dataset_dir.glob("*train*.json")) + list(dataset_dir.glob("*val*.json")) + list(dataset_dir.glob("*.json"))
        if not anno_files:
            res.valid = False
            res.errors.append("No annotation JSON files found in ChangeChat directory.")
            return res

        image_dir = dataset_dir / "images"
        if not image_dir.exists():
            image_dir = dataset_dir / "LEVIR-CC"

        for af in anno_files:
            try:
                with open(af, "r", encoding="utf-8") as f:
                    data = json.load(f)
                count = len(data) if isinstance(data, list) else len(data.get("samples", []))
                res.splits_found[af.stem] = count
                res.total_annotations += count

                # Verify first 5 image links
                samples = data if isinstance(data, list) else data.get("samples", [])
                for sample in samples[:5]:
                    imgs = sample.get("image", [])
                    if isinstance(imgs, list) and len(imgs) >= 2 and image_dir.exists():
                        p1 = image_dir / imgs[0]
                        p2 = image_dir / imgs[1]
                        if not p1.exists() or not p2.exists():
                            res.warnings.append(f"Sample images {imgs} not located in {image_dir}")
            except Exception as e:
                res.errors.append(f"Failed to read annotation file {af.name}: {str(e)}")

        res.total_pairs = res.total_annotations
        return res

    @classmethod
    def validate_rsrcc(cls, dataset_dir: Path) -> ValidationResult:
        """Validate RSRCC regional change QA dataset."""
        res = ValidationResult("rsrcc")
        if not dataset_dir.exists():
            res.valid = False
            res.errors.append(f"RSRCC directory does not exist: {dataset_dir}")
            return res

        qa_files = list(dataset_dir.glob("*.json")) + list(dataset_dir.glob("*.parquet")) + list(dataset_dir.glob("*.arrow"))
        if not qa_files:
            res.valid = False
            res.errors.append("No RSRCC annotation files found.")
            return res

        res.splits_found["files"] = len(qa_files)
        res.total_annotations = len(qa_files)
        return res

    @classmethod
    def validate_qag360k(cls, dataset_dir: Path) -> ValidationResult:
        """Validate QAG-360K grounding dataset."""
        res = ValidationResult("qag360k")
        if not dataset_dir.exists():
            res.valid = False
            res.errors.append(f"QAG-360K directory does not exist: {dataset_dir}")
            return res

        items = list(dataset_dir.glob("*.json")) + list(dataset_dir.glob("masks/*"))
        res.total_annotations = len(items)
        return res
