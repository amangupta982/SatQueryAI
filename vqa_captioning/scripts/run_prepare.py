#!/usr/bin/env python3
"""
CLI script to prepare, validate, and normalize BigEarthNet.txt annotations
into the unified SatQuery format.
Usage:
    python vqa_captioning/scripts/run_prepare.py --dataset /path/to/BigEarthNet.txt --output-dir /path/to/prepared_dataset
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from vqa_captioning.preprocessing.bigearthnet_parser import BigEarthNetParser
from vqa_captioning.preprocessing.sample_validator import SampleValidator
from vqa_captioning.preprocessing.data_statistics import DatasetStatistics

def main():
    parser = argparse.ArgumentParser(description="Prepare and validate BigEarthNet.txt dataset.")
    parser.add_argument("--dataset", type=str, required=True, help="Path to input dataset file or directory")
    parser.add_argument("--output-dir", type=str, default="data/prepared_satquery_vqa", help="Output directory for normalized samples")
    parser.add_argument("--skip-image-check", action="store_true", help="Skip verifying image paths exist on disk")

    args = parser.parse_args()

    input_path = Path(args.dataset)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading and parsing dataset from: {input_path}")
    bn_parser = BigEarthNetParser(dataset_dir=input_path if input_path.is_dir() else input_path.parent)
    validator = SampleValidator(check_image_exists=not args.skip_image_check)

    samples = []
    if input_path.is_file():
        samples = bn_parser.parse_file(input_path)
    else:
        for ext in ["*.json", "*.jsonl", "*.parquet"]:
            for f in input_path.glob(f"**/{ext}"):
                try:
                    samples.extend(bn_parser.parse_file(f))
                except Exception as e:
                    print(f"Warning: Failed to parse {f}: {e}")

    print(f"Parsed {len(samples)} total raw samples. Running validation...")
    valid_samples = []
    split_buckets: Dict[str, List[Dict]] = {"train": [], "validation": [], "test": [], "benchmark": []}

    for s in samples:
        s_dict = s.model_dump()
        is_valid, reason = validator.validate_sample(s_dict)
        if is_valid:
            valid_samples.append(s)
            split = s.metadata.split or "train"
            if split in split_buckets:
                split_buckets[split].append(s_dict)
            else:
                split_buckets.setdefault(split, []).append(s_dict)

    print(f"Validation complete: {len(valid_samples)} valid samples ({len(samples) - len(valid_samples)} rejected).")

    # Save prepared splits
    for split_name, records in split_buckets.items():
        if records:
            out_file = output_dir / f"{split_name}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
            print(f"Saved {split_name} split ({len(records)} samples) -> {out_file}")

    # Generate & save statistics report
    stats_calculator = DatasetStatistics(valid_samples)
    report_md = stats_calculator.generate_report()
    stats_file = output_dir / "dataset_statistics.md"
    with open(stats_file, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Saved statistics report -> {stats_file}")
    print("\nDataset preparation finished successfully.")

if __name__ == "__main__":
    main()
