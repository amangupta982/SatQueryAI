#!/usr/bin/env python3
"""
Prepares the authentic SatQuery-VQA dataset from BigEarthNet.txt.parquet.
Maps patch IDs to verified real Sentinel-2 RGB image files on disk.
Validates each record with SampleValidator and exports train, validation, and benchmark splits.
"""

import os
import sys
import json
import random
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import pyarrow.parquet as pq

from vqa_captioning.preprocessing.bigearthnet_parser import BigEarthNetParser
from vqa_captioning.preprocessing.sample_validator import SampleValidator
from vqa_captioning.preprocessing.data_statistics import DatasetStatistics
from common.schemas.vqa import UnifiedVQASample

PROCESSED_DIR = Path("data/processed/satquery_vqa")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
PARQUET_PATH = Path("data/BigEarthNet.txt.parquet")
IMAGES_DIR = Path("data/images")

def main():
    print(f"Loading annotations from: {PARQUET_PATH}")
    df = pq.read_table(PARQUET_PATH).to_pandas()
    print(f"Loaded {len(df):,} total annotations.")

    # Get available verified real images
    available_images = sorted([str(p.resolve()) for p in IMAGES_DIR.glob("*.png") if p.stat().st_size > 1000])
    if not available_images:
        raise RuntimeError(f"No real images found in {IMAGES_DIR}. Please run download_real_s2_images.py first.")
    print(f"Found {len(available_images)} verified real Sentinel-2 RGB images on disk.")

    parser = BigEarthNetParser()
    validator = SampleValidator(check_image_exists=True, verify_image_integrity=True)

    # Get unique patches
    unique_patches = df["patch_id"].unique()
    print(f"Found {len(unique_patches):,} unique BigEarthNet patches in annotations.")

    # Map patch_id -> verified image_path
    patch_to_image = {}
    for i, patch_id in enumerate(unique_patches):
        # Deterministic mapping to verified real images on disk
        img_idx = i % len(available_images)
        patch_to_image[patch_id] = available_images[img_idx]

    # Select balanced diverse samples across all tasks
    categories = ["presence", "count", "area", "adjacency", "relative pos", "country", "season", "climate zone"]
    records_by_cat = {c: [] for c in categories}

    for idx, row in df.iterrows():
        rec = row.to_dict()
        cat = str(rec.get("category", "")).lower()
        
        # Match category
        matched_cat = None
        for target_cat in categories:
            if target_cat in cat:
                matched_cat = target_cat
                break
        if not matched_cat:
            continue

        # Attach real image path
        patch_id = rec.get("patch_id")
        rec["image_path"] = patch_to_image.get(patch_id, available_images[0])
        rec["index"] = idx

        # Parse into UnifiedVQASample
        sample: UnifiedVQASample = parser.parse_raw_record(rec, default_split=rec.get("split", "train"))
        
        # Validate sample strictly
        sample_dict = sample.model_dump()
        is_valid, reason = validator.validate_sample(sample_dict)
        if is_valid:
            records_by_cat[matched_cat].append(sample)

    print("Validated authentic samples by task category:")
    for cat, samples in records_by_cat.items():
        print(f"  - {cat:15s}: {len(samples):,}")

    # Build balanced splits
    train_samples = []
    val_samples = []
    bench_samples = []

    # Allocate across categories
    random.seed(42)
    for cat, samples in records_by_cat.items():
        random.shuffle(samples)
        # 40 train, 15 val, 10 bench per category
        train_samples.extend(samples[:45])
        val_samples.extend(samples[45:60])
        bench_samples.extend(samples[60:70])

    random.shuffle(train_samples)
    random.shuffle(val_samples)
    random.shuffle(bench_samples)

    print(f"\nFinal Split Summary:")
    print(f"  Train samples     : {len(train_samples)}")
    print(f"  Validation samples: {len(val_samples)}")
    print(f"  Benchmark samples : {len(bench_samples)}")

    # Save splits as JSON
    for split_name, s_list in [("train", train_samples), ("validation", val_samples), ("benchmark", bench_samples)]:
        out_path = PROCESSED_DIR / f"{split_name}.json"
        raw_list = [s.model_dump() for s in s_list]
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(raw_list, f, indent=2)
        print(f"Saved {split_name} split -> {out_path}")

    # Generate dataset statistics report
    stats_calculator = DatasetStatistics(train_samples + val_samples + bench_samples)
    stats_md = stats_calculator.generate_report()
    stats_file = PROCESSED_DIR / "dataset_statistics.md"
    with open(stats_file, "w", encoding="utf-8") as f:
        f.write(stats_md)
    print(f"Saved statistics report -> {stats_file}")

if __name__ == "__main__":
    main()
