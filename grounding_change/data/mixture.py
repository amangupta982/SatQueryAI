"""
Dataset Mixture and Task-Balanced Sampling.
Implements configurable sampling across datasets:
ChangeChat-105k, RSRCC, QAG-360K, SECOND, BigEarthNet, RSVLM-QA.
Supports batch collation with partial annotations for multi-task training.
"""

import random
from typing import Any, Dict, List, Optional, Tuple
import torch
from torch.utils.data import Dataset, DataLoader
from .adapters.base import BaseChangeDataset


DEFAULT_MIXTURE_WEIGHTS = {
    "changechat": 0.30,
    "rsrcc": 0.20,
    "qag360k": 0.20,
    "second": 0.20,
    "bigearthnet": 0.05,
    "rsvlmqa": 0.05,
}


class DatasetMixture(Dataset):
    """
    Combines multiple heterogeneous datasets according to configured weights.
    Balances tasks (VQA, semantic segmentation, grounding) to avoid catastrophic forgetting.
    """

    def __init__(
        self,
        datasets: Dict[str, BaseChangeDataset],
        weights: Optional[Dict[str, float]] = None,
        total_samples: int = 10000,
    ):
        super().__init__()
        self.datasets = {k: v for k, v in datasets.items() if len(v) > 0}
        self.total_samples = total_samples

        if not self.datasets:
            # Fallback placeholder dataset
            self.dataset_keys = []
            self.normalized_weights = []
            return

        self.dataset_keys = list(self.datasets.keys())
        raw_weights = [
            (weights or DEFAULT_MIXTURE_WEIGHTS).get(k, 1.0 / len(self.dataset_keys))
            for k in self.dataset_keys
        ]
        total_w = sum(raw_weights)
        self.normalized_weights = [w / total_w for w in raw_weights]

    def __len__(self) -> int:
        if not self.datasets:
            return 0
        return self.total_samples

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        if not self.datasets:
            raise IndexError("No active datasets in mixture.")

        # Sample a dataset based on weights
        chosen_key = random.choices(self.dataset_keys, weights=self.normalized_weights, k=1)[0]
        ds = self.datasets[chosen_key]
        item_idx = random.randint(0, len(ds) - 1)
        sample = ds[item_idx]

        # If sample is not yet a dict (e.g. un-transformed TemporalVQASample), convert it
        if hasattr(sample, "model_dump"):
            return sample.model_dump()
        return sample


def collate_temporal_batch(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Collate function supporting partial annotations across multi-task batches.
    Stacks available tensors and pads/masks missing labels.
    """
    sample_ids = [item.get("sample_id", f"sample_{i}") for i, item in enumerate(batch)]
    questions = [item.get("question", "") for item in batch]
    answers = [item.get("answer", "") for item in batch]
    metas = [item.get("metadata", {}) for item in batch]

    # Stack image tensors (always present)
    t1_list = [item["t1"] if isinstance(item.get("t1"), torch.Tensor) else torch.zeros(3, 512, 512) for item in batch]
    t2_list = [item["t2"] if isinstance(item.get("t2"), torch.Tensor) else torch.zeros(3, 512, 512) for item in batch]
    has_t2 = torch.tensor([bool(item.get("has_t2", True)) for item in batch], dtype=torch.bool)

    t1_stacked = torch.stack(t1_list, dim=0)
    t2_stacked = torch.stack(t2_list, dim=0)

    collated: Dict[str, Any] = {
        "sample_ids": sample_ids,
        "t1": t1_stacked,
        "t2": t2_stacked,
        "has_t2": has_t2,
        "questions": questions,
        "answers": answers,
        "metadata": metas,
    }

    # Binary change mask
    has_change_mask = [item.get("change_mask") is not None for item in batch]
    collated["has_change_mask"] = torch.tensor(has_change_mask, dtype=torch.bool)
    if any(has_change_mask):
        first_mask = next(item["change_mask"] for item in batch if item.get("change_mask") is not None)
        h, w = first_mask.shape[-2:]
        masks = [item["change_mask"] if item.get("change_mask") is not None else torch.zeros((h, w), dtype=torch.long) for item in batch]
        collated["change_mask"] = torch.stack(masks, dim=0)

    # Semantic masks (T1, T2)
    has_sem = [item.get("semantic_mask_t1") is not None and item.get("semantic_mask_t2") is not None for item in batch]
    collated["has_semantic_mask"] = torch.tensor(has_sem, dtype=torch.bool)
    if any(has_sem):
        first_m = next(item["semantic_mask_t1"] for item in batch if item.get("semantic_mask_t1") is not None)
        h, w = first_m.shape[-2:]
        m1s = [item["semantic_mask_t1"] if item.get("semantic_mask_t1") is not None else torch.zeros((h, w), dtype=torch.long) for item in batch]
        m2s = [item["semantic_mask_t2"] if item.get("semantic_mask_t2") is not None else torch.zeros((h, w), dtype=torch.long) for item in batch]
        collated["semantic_mask_t1"] = torch.stack(m1s, dim=0)
        collated["semantic_mask_t2"] = torch.stack(m2s, dim=0)

    # Transition mask
    has_trans = [item.get("transition_mask") is not None for item in batch]
    collated["has_transition_mask"] = torch.tensor(has_trans, dtype=torch.bool)
    if any(has_trans):
        first_m = next(item["transition_mask"] for item in batch if item.get("transition_mask") is not None)
        h, w = first_m.shape[-2:]
        m_trans = [item["transition_mask"] if item.get("transition_mask") is not None else torch.zeros((h, w), dtype=torch.long) for item in batch]
        collated["transition_mask"] = torch.stack(m_trans, dim=0)

    # Grounding mask
    has_ground = [item.get("grounding_mask") is not None for item in batch]
    collated["has_grounding_mask"] = torch.tensor(has_ground, dtype=torch.bool)
    if any(has_ground):
        first_m = next(item["grounding_mask"] for item in batch if item.get("grounding_mask") is not None)
        h, w = first_m.shape[-2:]
        m_ground = [item["grounding_mask"] if item.get("grounding_mask") is not None else torch.zeros((h, w), dtype=torch.float) for item in batch]
        collated["grounding_mask"] = torch.stack(m_ground, dim=0)

    return collated
