"""
Dataset Inspector for BigEarthNet.txt and local remote-sensing dataset directories.
Audits directory structures, modalities, splits, sample validity, and image resolutions.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image

from vqa_captioning.preprocessing.bigearthnet_parser import BigEarthNetParser
from vqa_captioning.preprocessing.sample_validator import SampleValidator
from vqa_captioning.preprocessing.data_statistics import DatasetStatistics
from common.schemas.vqa import UnifiedVQASample

logger = logging.getLogger(__name__)

class DatasetInspector:
    """Audits and validates an entire dataset directory or file set."""

    def __init__(self, dataset_path: str, check_images: bool = True):
        self.dataset_path = Path(dataset_path)
        self.check_images = check_images
        self.parser = BigEarthNetParser(dataset_dir=self.dataset_path)
        self.validator = SampleValidator(check_image_exists=check_images, verify_image_integrity=False)

    def inspect(self) -> Dict[str, Any]:
        """Run comprehensive inspection on the dataset directory."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset path does not exist: {self.dataset_path}")

        report = {
            "dataset_path": str(self.dataset_path),
            "is_directory": self.dataset_path.is_dir(),
            "discovered_files": [],
            "image_pairs_count": 0,
            "total_annotations": 0,
            "modalities_detected": set(),
            "s1_info": {},
            "s2_info": {},
            "splits": {},
            "missing_images": 0,
            "malformed_annotations": 0,
            "duplicate_ids": 0,
            "validation_errors": [],
            "sample_dimensions": None,
            "statistics": {},
        }

        all_samples: List[UnifiedVQASample] = []

        if self.dataset_path.is_file():
            # Single annotation file
            report["discovered_files"].append(str(self.dataset_path.name))
            parsed = self.parser.parse_file(self.dataset_path)
            all_samples.extend(parsed)
        else:
            # Search for JSON, JSONL, Parquet annotation files
            for ext in ["*.json", "*.jsonl", "*.parquet"]:
                for file_path in self.dataset_path.glob(f"**/{ext}"):
                    # Skip config/internal files
                    if "package" in file_path.name or "metadata" in file_path.name:
                        continue
                    report["discovered_files"].append(str(file_path.relative_to(self.dataset_path)))

                    # Infer split from filename if possible
                    name_lower = file_path.stem.lower()
                    if "bench" in name_lower:
                        split = "benchmark"
                    elif "val" in name_lower:
                        split = "validation"
                    elif "test" in name_lower:
                        split = "test"
                    elif "train" in name_lower:
                        split = "train"
                    else:
                        split = "default"

                    try:
                        parsed = self.parser.parse_file(file_path, split=split)
                        all_samples.extend(parsed)
                    except Exception as e:
                        logger.warning(f"Could not parse {file_path}: {e}")

            # Check for image directories (Sentinel-1, Sentinel-2)
            s2_dirs = list(self.dataset_path.glob("**/Sentinel-2*")) + list(self.dataset_path.glob("**/BigEarthNet-S2*")) + list(self.dataset_path.glob("**/images*"))
            s1_dirs = list(self.dataset_path.glob("**/Sentinel-1*")) + list(self.dataset_path.glob("**/BigEarthNet-S1*")) + list(self.dataset_path.glob("**/sar*"))

            if s2_dirs:
                report["modalities_detected"].add("Sentinel-2 (Optical)")
                report["s2_info"]["directory"] = str(s2_dirs[0].relative_to(self.dataset_path))
            if s1_dirs:
                report["modalities_detected"].add("Sentinel-1 (SAR)")
                report["s1_info"]["directory"] = str(s1_dirs[0].relative_to(self.dataset_path))

        # Validate samples
        valid_samples = []
        for sample in all_samples:
            sample_dict = sample.model_dump()
            is_valid, reason = self.validator.validate_sample(sample_dict)
            if is_valid:
                valid_samples.append(sample)
                # Inspect dimensions from first valid image
                if report["sample_dimensions"] is None and self.check_images and sample.image_path and os.path.exists(sample.image_path):
                    try:
                        with Image.open(sample.image_path) as img:
                            report["sample_dimensions"] = f"{img.width}x{img.height}"
                    except Exception:
                        pass
            else:
                if "Duplicate" in reason:
                    report["duplicate_ids"] += 1
                elif "not found" in reason:
                    report["missing_images"] += 1
                else:
                    report["malformed_annotations"] += 1
                if len(report["validation_errors"]) < 20:
                    report["validation_errors"].append({"sample_id": sample.sample_id, "reason": reason})

        report["total_annotations"] = len(all_samples)
        report["valid_annotations"] = len(valid_samples)
        report["modalities_detected"] = list(report["modalities_detected"])

        # Compute statistics on valid samples
        stats_calc = DatasetStatistics(valid_samples)
        report["statistics"] = stats_calc.compute()
        report["image_pairs_count"] = report["statistics"].get("total_unique_patches", 0)

        return report

    def print_inspection_report(self, report: Optional[Dict[str, Any]] = None) -> str:
        """Format the report into a console-friendly string."""
        if report is None:
            report = self.inspect()

        lines = [
            "==================================================================",
            "                SATQUERY-VQA DATASET AUDIT REPORT                 ",
            "==================================================================",
            f"Dataset Path        : {report['dataset_path']}",
            f"Discovered Files    : {len(report['discovered_files'])} annotation files",
            f"Total Annotations   : {report['total_annotations']:,}",
            f"Valid Annotations   : {report['valid_annotations']:,}",
            f"Unique Patches      : {report['image_pairs_count']:,}",
            f"Modalities Detected : {', '.join(report['modalities_detected']) or 'Sentinel-2 (Optical inferred)'}",
            f"Sample Resolution   : {report['sample_dimensions'] or '120x120 (Standard BigEarthNet)'}",
            "",
            "--- Quality Assurance Summary ---",
            f"Missing Images      : {report['missing_images']}",
            f"Duplicate IDs       : {report['duplicate_ids']}",
            f"Malformed Samples   : {report['malformed_annotations']}",
            "",
            "--- Split Breakdown ---",
        ]

        splits = report["statistics"].get("split_distribution", {})
        for split_name, count in splits.items():
            lines.append(f"  - {split_name:<15}: {count:,}")

        lines.append("")
        lines.append("--- Task Breakdown ---")
        tasks = report["statistics"].get("task_distribution", {})
        for task_name, count in tasks.items():
            lines.append(f"  - {task_name:<25}: {count:,}")

        lines.append("==================================================================")
        return "\n".join(lines)
