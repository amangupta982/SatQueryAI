import argparse
import logging
import sys

from .config import config
from .loader import load_bigearthnet_annotations
from .filtering import filter_annotations
from .grouping import group_annotations_by_pair
from .sampler import sample_image_pairs
from .manifest import generate_manifest_and_annotations
from .downloader import MockDownloader, download_images_for_manifest
from .validator import validate_dataset_preparation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Prepare BigEarthNet dataset subset")
    parser.add_argument("--max-pairs", type=int, default=config.DATASET_MAX_PAIRS, help="Maximum number of unique image pairs to select")
    parser.add_argument("--split", type=str, help="Filter by specific split (e.g., train, validation, test)")
    parser.add_argument("--task", type=str, help="Filter by specific task (e.g., vqa, grounding)")
    parser.add_argument("--seed", type=int, default=config.DATASET_SEED, help="Random seed for reproducible sampling")
    parser.add_argument("--output-dir", type=str, default=config.DATASET_OUTPUT_DIR, help="Output directory for the dataset")
    
    args = parser.parse_args()
    
    logger.info("Starting BigEarthNet dataset preparation")
    logger.info(f"Configuration: max_pairs={args.max_pairs}, split={args.split}, task={args.task}, seed={args.seed}, output_dir={args.output_dir}")

    # 1. Load & Filter
    records = load_bigearthnet_annotations()
    filtered_records = filter_annotations(records, target_split=args.split, target_task=args.task)
    
    # 2. Group
    logger.info(f"Grouping annotations by unique image pairs (early stopping at {args.max_pairs} pairs)...")
    grouped_pairs = group_annotations_by_pair(filtered_records, max_pairs=args.max_pairs, seed=args.seed)
    total_unique_pairs = len(grouped_pairs)
    logger.info(f"Found {total_unique_pairs} unique image pairs after filtering.")

    if total_unique_pairs == 0:
        logger.warning("No pairs found matching criteria. Exiting.")
        sys.exit(0)

    # 3. Sample
    logger.info(f"Sampling up to {args.max_pairs} pairs with seed {args.seed}...")
    sampled_pairs = sample_image_pairs(grouped_pairs, max_pairs=args.max_pairs, seed=args.seed)
    selected_pair_count = len(sampled_pairs)
    
    total_annotations_selected = sum(len(anns) for anns in sampled_pairs.values())
    logger.info(f"Selected {selected_pair_count} unique image pairs containing {total_annotations_selected} annotations.")

    # 4. Manifest
    logger.info("Generating manifest and annotations files...")
    manifest_path, annotations_path = generate_manifest_and_annotations(sampled_pairs, args.output_dir)
    logger.info(f"Manifest written to {manifest_path}")
    
    # 5. Download (Mock)
    logger.info("Starting image download process...")
    downloader = MockDownloader()
    download_images_for_manifest(manifest_path, args.output_dir, downloader)
    
    # 6. Validate
    logger.info("Validating dataset preparation...")
    is_valid = validate_dataset_preparation(args.output_dir)
    
    if is_valid:
        logger.info("Dataset preparation completed successfully.")
    else:
        logger.error("Dataset preparation failed validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
