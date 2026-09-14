import os
import json
import logging

logger = logging.getLogger(__name__)

def validate_dataset_preparation(output_dir: str) -> bool:
    """
    Validates that the dataset preparation was successful:
    1. manifest.jsonl and annotations.jsonl exist.
    2. Image files listed in manifest exist.
    """
    manifest_path = os.path.join(output_dir, "manifest.jsonl")
    annotations_path = os.path.join(output_dir, "annotations.jsonl")

    if not os.path.exists(manifest_path):
        logger.error(f"Validation failed: Missing {manifest_path}")
        return False
    if not os.path.exists(annotations_path):
        logger.error(f"Validation failed: Missing {annotations_path}")
        return False

    valid = True
    pair_ids = set()
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            record = json.loads(line)
            pair_id = record['pair_id']
            
            if pair_id in pair_ids:
                logger.error(f"Validation failed: Duplicate pair_id {pair_id} found in manifest")
                valid = False
            pair_ids.add(pair_id)

            opt_full = os.path.join(output_dir, record['optical_path'])
            sar_full = os.path.join(output_dir, record['sar_path'])

            if not os.path.exists(opt_full):
                logger.error(f"Validation failed: Missing optical image {opt_full}")
                valid = False
            if not os.path.exists(sar_full):
                logger.error(f"Validation failed: Missing SAR image {sar_full}")
                valid = False
                
    logger.info(f"Validation complete. Valid: {valid}")
    return valid
