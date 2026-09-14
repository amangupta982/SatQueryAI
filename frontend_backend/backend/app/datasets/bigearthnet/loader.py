from datasets import load_dataset
from typing import Iterator, Dict, Any
import logging

from .config import config

logger = logging.getLogger(__name__)

def load_bigearthnet_annotations() -> Iterator[Dict[str, Any]]:
    """
    Lazily load the BigEarthNet text annotations dataset from Hugging Face.
    Yields raw dictionary records.
    """
    dataset_name = config.DATASET_NAME
    logger.info(f"Loading dataset {dataset_name} in streaming mode")
    try:
        dataset = load_dataset(dataset_name, split="all_data", streaming=True)
        for row in dataset:
            yield row
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise
