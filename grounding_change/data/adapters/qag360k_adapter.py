"""
Adapter for QAG-360K / VisTA Visual Grounding Dataset.
Connects Question + Answer + Grounding Mask for category-specific change localization.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from PIL import Image
import numpy as np

from .base import ChangeGroundingDataset
from ...schemas import TemporalVQASample


class QAG360KAdapter(ChangeGroundingDataset):
    """Adapter for QAG-360K grounding triplets."""

    def __init__(
        self,
        dataset_dir: Path,
        split: str = "train",
        transform: Optional[Callable] = None,
        max_samples: Optional[int] = None,
    ):
        super().__init__(dataset_dir, split, transform, max_samples)
        self._load_annotations()

    def _load_annotations(self):
        json_candidates = list(self.dataset_dir.glob(f"*{self.split}*.json")) + list(self.dataset_dir.glob("*.json"))
        if not json_candidates:
            return

        try:
            with open(json_candidates[0], "r", encoding="utf-8") as f:
                data = json.load(f)
            self.samples = data if isinstance(data, list) else data.get("samples", [])
        except Exception as e:
            print(f"Error loading QAG-360K annotations: {e}")

    def __getitem__(self, idx: int) -> TemporalVQASample:
        item = self.samples[idx]
        sample_id = str(item.get("id", f"qag_{idx}"))

        img_t1 = item.get("image_t1", item.get("im1", ""))
        img_t2 = item.get("image_t2", item.get("im2", None))
        question = item.get("question", item.get("text_query", "Where is the changed area?"))
        answer = item.get("answer", "Here is the localized change region.")

        # Grounding mask path
        mask_path = item.get("mask_path", None)
        grounding_mask = None
        if mask_path and Path(mask_path).exists():
            try:
                grounding_mask = np.array(Image.open(mask_path)).astype(np.uint8)
            except Exception:
                pass

        sample = TemporalVQASample(
            sample_id=sample_id,
            image_t1=str(img_t1),
            image_t2=str(img_t2) if img_t2 else None,
            question=question,
            answer=answer,
            grounding_mask=grounding_mask,
            metadata={"dataset": "qag360k", "category": item.get("category", "")}
        )

        if self.transform:
            sample = self.transform(sample)

        return sample
