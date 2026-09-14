"""
Transforms and Paired Augmentations for Bi-Temporal Remote Sensing Data.
Ensures consistent spatial operations across T1, T2, and ground-truth masks.
"""

import random
from typing import Any, Dict, List, Optional, Tuple, Union
import torch
import torchvision.transforms.functional as TF
from PIL import Image
import numpy as np
from ..schemas import TemporalVQASample


class PairedTemporalTransform:
    """
    Applies identical geometric and photometric transformations to
    bi-temporal pairs (T1, T2) and their corresponding spatial masks.
    """

    def __init__(
        self,
        img_size: int = 512,
        is_training: bool = True,
        mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
        std: Tuple[float, float, float] = (0.229, 0.224, 0.225),
    ):
        self.img_size = img_size
        self.is_training = is_training
        self.mean = mean
        self.std = std

    def _load_image(self, img_input: Union[str, np.ndarray, Image.Image, torch.Tensor]) -> Image.Image:
        """Helper to convert diverse inputs to PIL RGB Image."""
        if isinstance(img_input, torch.Tensor):
            arr = img_input.detach().cpu().numpy()
            if arr.ndim == 3 and arr.shape[0] in [1, 3]:
                arr = np.transpose(arr, (1, 2, 0))
            return Image.fromarray((arr * 255).astype(np.uint8) if arr.max() <= 1.0 else arr.astype(np.uint8))
        elif isinstance(img_input, np.ndarray):
            return Image.fromarray(img_input.astype(np.uint8)).convert("RGB")
        elif isinstance(img_input, str):
            try:
                return Image.open(img_input).convert("RGB")
            except Exception:
                # Synthetic dummy image fallback if path is placeholder or missing
                return Image.new("RGB", (self.img_size, self.img_size), color=(100, 100, 100))
        elif isinstance(img_input, Image.Image):
            return img_input.convert("RGB")
        return Image.new("RGB", (self.img_size, self.img_size), color=(100, 100, 100))

    def _to_mask_image(self, mask_input: Optional[Union[np.ndarray, Image.Image]]) -> Optional[Image.Image]:
        if mask_input is None:
            return None
        if isinstance(mask_input, Image.Image):
            return mask_input
        if isinstance(mask_input, np.ndarray):
            return Image.fromarray(mask_input.astype(np.uint8))
        return None

    def __call__(self, sample: TemporalVQASample) -> Dict[str, Any]:
        img1 = self._load_image(sample.image_t1)
        img2 = self._load_image(sample.image_t2) if sample.image_t2 else img1.copy()

        m_change = self._to_mask_image(sample.change_mask)
        m_sem1 = self._to_mask_image(sample.semantic_mask_t1)
        m_sem2 = self._to_mask_image(sample.semantic_mask_t2)
        m_trans = self._to_mask_image(sample.transition_mask)
        m_ground = self._to_mask_image(sample.grounding_mask)

        # 1. Resize
        img1 = TF.resize(img1, [self.img_size, self.img_size], interpolation=TF.InterpolationMode.BILINEAR)
        img2 = TF.resize(img2, [self.img_size, self.img_size], interpolation=TF.InterpolationMode.BILINEAR)
        if m_change:
            m_change = TF.resize(m_change, [self.img_size, self.img_size], interpolation=TF.InterpolationMode.NEAREST)
        if m_sem1:
            m_sem1 = TF.resize(m_sem1, [self.img_size, self.img_size], interpolation=TF.InterpolationMode.NEAREST)
        if m_sem2:
            m_sem2 = TF.resize(m_sem2, [self.img_size, self.img_size], interpolation=TF.InterpolationMode.NEAREST)
        if m_trans:
            m_trans = TF.resize(m_trans, [self.img_size, self.img_size], interpolation=TF.InterpolationMode.NEAREST)
        if m_ground:
            m_ground = TF.resize(m_ground, [self.img_size, self.img_size], interpolation=TF.InterpolationMode.NEAREST)

        # 2. Random Flips if training
        if self.is_training:
            if random.random() > 0.5:
                img1 = TF.hflip(img1)
                img2 = TF.hflip(img2)
                if m_change: m_change = TF.hflip(m_change)
                if m_sem1: m_sem1 = TF.hflip(m_sem1)
                if m_sem2: m_sem2 = TF.hflip(m_sem2)
                if m_trans: m_trans = TF.hflip(m_trans)
                if m_ground: m_ground = TF.hflip(m_ground)

            if random.random() > 0.5:
                img1 = TF.vflip(img1)
                img2 = TF.vflip(img2)
                if m_change: m_change = TF.vflip(m_change)
                if m_sem1: m_sem1 = TF.vflip(m_sem1)
                if m_sem2: m_sem2 = TF.vflip(m_sem2)
                if m_trans: m_trans = TF.vflip(m_trans)
                if m_ground: m_ground = TF.vflip(m_ground)

        # 3. Convert to tensor & normalize
        t1_tensor = TF.to_tensor(img1)
        t2_tensor = TF.to_tensor(img2)
        t1_norm = TF.normalize(t1_tensor, mean=self.mean, std=self.std)
        t2_norm = TF.normalize(t2_tensor, mean=self.mean, std=self.std)

        # Masks to Long/Float Tensors
        tensor_dict: Dict[str, Any] = {
            "sample_id": sample.sample_id,
            "t1": t1_norm,
            "t2": t2_norm,
            "has_t2": sample.image_t2 is not None,
            "question": sample.question or "",
            "answer": sample.answer or "",
            "metadata": sample.metadata,
        }

        if m_change is not None:
            tensor_dict["change_mask"] = torch.from_numpy(np.array(m_change)).long()
        if m_sem1 is not None:
            tensor_dict["semantic_mask_t1"] = torch.from_numpy(np.array(m_sem1)).long()
        if m_sem2 is not None:
            tensor_dict["semantic_mask_t2"] = torch.from_numpy(np.array(m_sem2)).long()
        if m_trans is not None:
            tensor_dict["transition_mask"] = torch.from_numpy(np.array(m_trans)).long()
        if m_ground is not None:
            tensor_dict["grounding_mask"] = torch.from_numpy(np.array(m_ground)).float()

        return tensor_dict
