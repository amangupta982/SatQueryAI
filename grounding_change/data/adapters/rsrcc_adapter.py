"""
Adapter for Google RSRCC (Remote Sensing Regional Change Comprehension).
Primary dataset for fine-grained regional change VQA.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import pandas as pd

from .base import MultitemporalVQADataset
from ...schemas import BoundingBox, TemporalVQASample


class RSRCCAdapter(MultitemporalVQADataset):
    """Adapter for Google RSRCC fine-grained change questions."""

    def __init__(
        self,
        dataset_dir: Path,
        split: str = "train",
        transform: Optional[Callable] = None,
        max_samples: Optional[int] = None,
    ):
        super().__init__(dataset_dir, split, transform, max_samples)
        self._load_data()

    def _load_data(self):
        # Try parquet, arrow, or json
        parquets = list(self.dataset_dir.glob(f"*{self.split}*.parquet")) + list(self.dataset_dir.glob("*.parquet"))
        if parquets:
            try:
                df = pd.read_parquet(parquets[0])
                self.samples = df.to_dict(orient="records")
                return
            except Exception as e:
                print(f"Error reading parquet {parquets[0]}: {e}")

        jsons = list(self.dataset_dir.glob(f"*{self.split}*.json")) + list(self.dataset_dir.glob("*.json"))
        if jsons:
            try:
                with open(jsons[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.samples = data if isinstance(data, list) else data.get("data", [])
            except Exception as e:
                print(f"Error reading JSON {jsons[0]}: {e}")

    def __getitem__(self, idx: int) -> TemporalVQASample:
        item = self.samples[idx]
        sample_id = str(item.get("id", item.get("sample_id", f"rsrcc_{idx}")))

        img_t1 = item.get("image_t1", item.get("t1_path", ""))
        img_t2 = item.get("image_t2", item.get("t2_path", ""))
        question = item.get("question", item.get("query", "What changed in this region?"))
        answer = str(item.get("answer", item.get("label", "")))

        # Region bounding box if provided
        bbox_raw = item.get("bbox", item.get("region_box", None))
        bboxes = None
        if bbox_raw and len(bbox_raw) == 4:
            bboxes = [BoundingBox(x_min=int(bbox_raw[0]), y_min=int(bbox_raw[1]), x_max=int(bbox_raw[2]), y_max=int(bbox_raw[3]))]

        sample = TemporalVQASample(
            sample_id=sample_id,
            image_t1=img_t1,
            image_t2=img_t2,
            question=question,
            answer=answer,
            bbox_targets=bboxes,
            metadata={"dataset": "rsrcc", "category": item.get("category", "building")}
        )

        if self.transform:
            sample = self.transform(sample)

        return sample
