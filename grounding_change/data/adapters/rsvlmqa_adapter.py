"""
Adapter for RSVLM-QA.
Supplementary dataset for remote-sensing VQA question diversity and robustness.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from .base import GeneralRemoteSensingVQADataset
from ...schemas import TemporalVQASample


class RSVLMQAAdapter(GeneralRemoteSensingVQADataset):
    """Adapter for RSVLM-QA dataset."""

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
        jsons = list(self.dataset_dir.glob("*.json"))
        if jsons:
            try:
                with open(jsons[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.samples = data if isinstance(data, list) else data.get("questions", [])
            except Exception as e:
                print(f"Error loading RSVLM-QA json: {e}")

    def __getitem__(self, idx: int) -> TemporalVQASample:
        item = self.samples[idx]
        sample = TemporalVQASample(
            sample_id=str(item.get("id", f"rsvlm_{idx}")),
            image_t1=item.get("image", ""),
            image_t2=None,
            question=item.get("question", "What is present in this image?"),
            answer=str(item.get("answer", "")),
            metadata={"dataset": "rsvlmqa"}
        )

        if self.transform:
            sample = self.transform(sample)

        return sample
