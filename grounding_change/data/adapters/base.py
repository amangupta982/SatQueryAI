"""
Base Dataset Classes for Remote-Sensing VQA and Change Understanding.
Standardizes task-oriented abstractions for multitemporal remote-sensing data.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import torch
from torch.utils.data import Dataset
from ...schemas import TemporalVQASample


class BaseChangeDataset(Dataset, ABC):
    """Abstract base class for all remote sensing datasets."""

    def __init__(
        self,
        dataset_dir: Path,
        split: str = "train",
        transform: Optional[Callable] = None,
        max_samples: Optional[int] = None,
    ):
        super().__init__()
        self.dataset_dir = Path(dataset_dir)
        self.split = split
        self.transform = transform
        self.max_samples = max_samples
        self.samples: List[Any] = []

    def __len__(self) -> int:
        if self.max_samples and self.max_samples > 0:
            return min(len(self.samples), self.max_samples)
        return len(self.samples)

    @abstractmethod
    def __getitem__(self, idx: int) -> TemporalVQASample:
        """Return a standardized TemporalVQASample."""
        pass


class MultitemporalVQADataset(BaseChangeDataset):
    """Interface for multitemporal question answering over T1/T2 image pairs (e.g. ChangeChat-105k, RSRCC)."""
    task_type: str = "vqa"


class SemanticChangeDataset(BaseChangeDataset):
    """Interface for pixel-level semantic change segmentation and transitions (e.g. SECOND)."""
    task_type: str = "semantic_change"


class ChangeGroundingDataset(BaseChangeDataset):
    """Interface for question-conditioned visual grounding and evidence masks (e.g. QAG-360K / VisTA)."""
    task_type: str = "grounding"


class GeneralRemoteSensingVQADataset(BaseChangeDataset):
    """Interface for single-image RS VQA and multimodal domain adaptation (e.g. BigEarthNet.txt, RSVLM-QA)."""
    task_type: str = "general_vqa"
