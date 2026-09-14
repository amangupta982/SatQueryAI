"""
Adapter for BigEarthNet.txt.
General remote-sensing multimodal understanding, domain adaptation, and single-image VQA.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from .base import GeneralRemoteSensingVQADataset
from ...schemas import TemporalVQASample


class BigEarthNetAdapter(GeneralRemoteSensingVQADataset):
    """Adapter for BigEarthNet.txt multimodal samples."""

    def __init__(
        self,
        dataset_dir: Path,
        split: str = "train",
        transform: Optional[Callable] = None,
        max_samples: Optional[int] = None,
    ):
        super().__init__(dataset_dir, split, transform, max_samples)
        self._load_files()

    def _load_files(self):
        txt_files = list(self.dataset_dir.glob("*.txt"))
        if txt_files:
            try:
                with open(txt_files[0], "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                self.samples = lines
            except Exception as e:
                print(f"Error reading BigEarthNet txt: {e}")

    def __getitem__(self, idx: int) -> TemporalVQASample:
        line = self.samples[idx]
        parts = line.split("\t")
        img_path = parts[0] if parts else ""
        caption = parts[1] if len(parts) > 1 else "Satellite image scene."

        sample = TemporalVQASample(
            sample_id=f"ben_{idx}",
            image_t1=img_path,
            image_t2=None,  # Single-image VQA sample
            question="What land cover is visible in this satellite image?",
            answer=caption,
            metadata={"dataset": "bigearthnet"}
        )

        if self.transform:
            sample = self.transform(sample)

        return sample
