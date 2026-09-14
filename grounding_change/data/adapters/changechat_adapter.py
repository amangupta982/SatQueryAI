"""
Adapter for ChangeChat-105k (DeltaVLM).
Primary interactive multitemporal VQA dataset.
Covers change captioning, classification, quantification, localization, and multi-turn dialogues.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from PIL import Image
import numpy as np

from .base import MultitemporalVQADataset
from ...schemas import TemporalVQASample


class ChangeChatAdapter(MultitemporalVQADataset):
    """Adapter transforming ChangeChat-105k annotations into TemporalVQASample."""

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
        # Look for split file or main JSON
        candidates = [
            self.dataset_dir / f"changechat_105k_{self.split}.json",
            self.dataset_dir / f"changechat_{self.split}.json",
            self.dataset_dir / "changechat_105k_train.json",
        ]
        target_file = None
        for c in candidates:
            if c.exists():
                target_file = c
                break

        if not target_file:
            # Check any json
            jsons = list(self.dataset_dir.glob("*.json"))
            if jsons:
                target_file = jsons[0]

        if not target_file:
            return

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.samples = data if isinstance(data, list) else data.get("samples", [])
        except Exception as e:
            print(f"Error loading ChangeChat annotations from {target_file}: {e}")
            self.samples = []

    def __getitem__(self, idx: int) -> TemporalVQASample:
        item = self.samples[idx]
        sample_id = str(item.get("id", f"cc_{idx}"))

        # Extract images
        image_paths = item.get("image", [])
        t1_path, t2_path = None, None
        img_dir = self.dataset_dir / "images"
        if not img_dir.exists():
            img_dir = self.dataset_dir / "LEVIR-CC"

        if isinstance(image_paths, list) and len(image_paths) >= 2:
            p1 = img_dir / image_paths[0]
            p2 = img_dir / image_paths[1]
            t1_path = str(p1) if p1.exists() else str(image_paths[0])
            t2_path = str(p2) if p2.exists() else str(image_paths[1])

        # Extract question & answer from conversations
        conversations = item.get("conversations", [])
        question = ""
        answer = ""
        for turn in conversations:
            speaker = turn.get("from", "").lower()
            val = turn.get("value", "").replace("<image>", "").strip()
            if speaker in ["human", "user"] and not question:
                question = val
            elif speaker in ["gpt", "assistant"] and not answer:
                answer = val

        change_flag = item.get("changeflag", 1)

        sample = TemporalVQASample(
            sample_id=sample_id,
            image_t1=t1_path or "",
            image_t2=t2_path,
            question=question or "What changed between the two images?",
            answer=answer or "Change observed in the scene.",
            metadata={
                "change_flag": change_flag,
                "dataset": "changechat",
                "turns_count": len(conversations),
                "all_conversations": conversations,
            }
        )

        if self.transform:
            sample = self.transform(sample)

        return sample
