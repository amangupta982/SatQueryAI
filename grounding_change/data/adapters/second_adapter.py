"""
Adapter for SECOND (Semantic Change Detection) benchmark.
Provides pixel-level semantic change supervision across 6 land-cover categories.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from PIL import Image
import numpy as np

from .base import SemanticChangeDataset
from ...schemas import TemporalVQASample
from ...taxonomy import taxonomy


# Map SECOND raw label indices (0 to 6) to taxonomy IDs
# SECOND classes: 0: background/unclassified, 1: non-vegetated ground (bare_land), 2: tree (vegetation),
# 3: low vegetation, 4: water, 5: buildings, 6: playgrounds (infrastructure)
SECOND_TO_TAXONOMY = {
    0: 0,  # background
    1: 5,  # bare_land
    2: 2,  # vegetation (tree)
    3: 3,  # low_vegetation
    4: 4,  # water
    5: 1,  # building
    6: 6,  # infrastructure (playgrounds)
}


class SECONDAdapter(SemanticChangeDataset):
    """Adapter for SECOND dataset generating paired masks and transitions."""

    def __init__(
        self,
        dataset_dir: Path,
        split: str = "train",
        transform: Optional[Callable] = None,
        max_samples: Optional[int] = None,
    ):
        super().__init__(dataset_dir, split, transform, max_samples)
        self._find_pairs()

    def _find_pairs(self):
        split_dir = self.dataset_dir / self.split
        if not split_dir.exists():
            split_dir = self.dataset_dir

        im1_dir = split_dir / "im1"
        im2_dir = split_dir / "im2"
        lbl1_dir = split_dir / "label1"
        lbl2_dir = split_dir / "label2"

        if not im1_dir.exists():
            return

        im1_files = sorted(list(im1_dir.glob("*.png")) + list(im1_dir.glob("*.jpg")) + list(im1_dir.glob("*.tif")))
        for f1 in im1_files:
            f2 = im2_dir / f1.name
            l1 = lbl1_dir / f1.name if lbl1_dir.exists() else None
            l2 = lbl2_dir / f1.name if lbl2_dir.exists() else None

            if f2.exists():
                self.samples.append({
                    "id": f1.stem,
                    "im1": f1,
                    "im2": f2,
                    "lbl1": l1 if (l1 and l1.exists()) else None,
                    "lbl2": l2 if (l2 and l2.exists()) else None,
                })

    def __getitem__(self, idx: int) -> TemporalVQASample:
        item = self.samples[idx]

        # Load labels if available to build change_mask and transition_mask
        sem_m1, sem_m2, change_m, trans_m = None, None, None, None

        if item["lbl1"] and item["lbl2"]:
            try:
                raw_m1 = np.array(Image.open(item["lbl1"]))
                raw_m2 = np.array(Image.open(item["lbl2"]))

                # Map to unified taxonomy
                sem_m1 = np.zeros_like(raw_m1, dtype=np.int64)
                sem_m2 = np.zeros_like(raw_m2, dtype=np.int64)
                for src_cls, dst_cls in SECOND_TO_TAXONOMY.items():
                    sem_m1[raw_m1 == src_cls] = dst_cls
                    sem_m2[raw_m2 == src_cls] = dst_cls

                # Binary change: pixels where class changed and neither is background (0)
                change_m = ((sem_m1 != sem_m2) & (sem_m1 > 0) & (sem_m2 > 0)).astype(np.uint8)

                # Transition mask encoded as (from_class * 100 + to_class) where change occurs
                trans_m = np.zeros_like(change_m, dtype=np.int64)
                changed_pixels = change_m > 0
                trans_m[changed_pixels] = sem_m1[changed_pixels] * 100 + sem_m2[changed_pixels]
            except Exception as e:
                print(f"Error loading SECOND labels: {e}")

        sample = TemporalVQASample(
            sample_id=str(item["id"]),
            image_t1=str(item["im1"]),
            image_t2=str(item["im2"]),
            change_mask=change_m,
            semantic_mask_t1=sem_m1,
            semantic_mask_t2=sem_m2,
            transition_mask=trans_m,
            metadata={"dataset": "second"}
        )

        if self.transform:
            sample = self.transform(sample)

        return sample
