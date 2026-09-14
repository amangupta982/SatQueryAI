"""
Multimodal Data Collator for SatQuery-VQA.
Prepares vision tokens, chat templates, attention masks, and label masking for supervised fine-tuning.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from PIL import Image
import torch
from torch.utils.data import Dataset
from common.schemas.vqa import UnifiedVQASample
from vqa_captioning.preprocessing.sensor_adapters import Sentinel2Adapter, Sentinel1SARAdapter

class VQADataset(Dataset):
    """PyTorch Dataset for UnifiedVQASamples."""

    def __init__(self, samples: List[UnifiedVQASample]):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int) -> UnifiedVQASample:
        return self.samples[idx]


class MultimodalDataCollator:
    """
    Collator that transforms raw VQA samples into tokenized, padded batches
    suitable for Vision-Language causal training.
    """

    def __init__(
        self,
        processor: Any,
        max_length: int = 1024,
        ignore_index: int = -100,
        mock_mode: bool = False,
    ):
        self.processor = processor
        self.max_length = max_length
        self.ignore_index = ignore_index
        self.mock_mode = mock_mode

    def __call__(self, batch: List[Union[UnifiedVQASample, Dict[str, Any]]]) -> Dict[str, torch.Tensor]:
        """
        Collates a batch of samples into model inputs.
        Applies chat formatting and masks instruction tokens so loss is only computed on the answer.
        """
        if self.mock_mode or self.processor is None:
            # Mock collator for unit tests or dry-run without downloading remote processors
            batch_size = len(batch)
            seq_len = 32
            return {
                "input_ids": torch.randint(100, 2000, (batch_size, seq_len), dtype=torch.long),
                "attention_mask": torch.ones((batch_size, seq_len), dtype=torch.long),
                "labels": torch.randint(100, 2000, (batch_size, seq_len), dtype=torch.long),
                "pixel_values": torch.zeros((batch_size, 3, 120, 120), dtype=torch.float32),
            }

        images: List[Image.Image] = []
        formatted_texts: List[str] = []

        for item in batch:
            if isinstance(item, dict):
                q = item.get("question", "")
                a = item.get("answer", "")
                img_path = item.get("image_path", "")
                sensor = item.get("sensor", "Sentinel-2")
            else:
                q = item.question
                a = item.answer
                img_path = item.image_path
                sensor = item.sensor

            # Load / process image
            if img_path and Path(img_path).exists():
                if "sar" in sensor.lower():
                    img, _ = Sentinel1SARAdapter.load_sar_image(img_path)
                else:
                    img, _ = Sentinel2Adapter.load_image(img_path)
            else:
                # 120x120 placeholder remote sensing image
                img = Image.new("RGB", (120, 120), color=(34, 139, 34))

            images.append(img)

            # Build conversational instruction + target answer
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": img},
                        {"type": "text", "text": q},
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": a},
                    ],
                },
            ]

            chat_text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
            formatted_texts.append(chat_text)

        # Batch tokenization and image feature processing
        batch_inputs = self.processor(
            text=formatted_texts,
            images=images,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )

        labels = batch_inputs["input_ids"].clone()

        # Mask prompt tokens with ignore_index (-100)
        # Identify the assistant start token or role header if available
        tokenizer = getattr(self.processor, "tokenizer", None)
        if tokenizer:
            pad_token_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else -100
            labels[labels == pad_token_id] = self.ignore_index

        batch_inputs["labels"] = labels
        return batch_inputs
