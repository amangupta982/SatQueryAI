"""
BigEarthNet.txt Multimodal Dataset Adapter
Paper: "BigEarthNet.txt: A Large-Scale Multi-Sensor Image-Text Dataset and Benchmark for Earth Observation"
arXiv: https://arxiv.org/abs/2603.29630
Portal: https://txt.bigearth.net/

Provides PyTorch Dataset and dataloading utilities for co-registered
Sentinel-1 SAR + Sentinel-2 Multispectral imagery paired with 15 tasks
spanning VQA, Referring Expression Grounding, and Captioning.
"""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from torch.utils.data import Dataset
from PIL import Image

from grounding_change.config import settings
from grounding_change.schemas import (
    BigEarthNetMultimodalSample,
    BoundingBox,
    SensorObservationMetadata,
    TemporalVQASample,
    AnalysisInterpretationMode,
)
from .base import BaseChangeDataset

logger = logging.getLogger("BigEarthNetAdapter")


class BigEarthNetTxtDataset(BaseChangeDataset):
    """
    Official PyTorch Dataset adapter for BigEarthNet.txt.
    Loads co-registered Sentinel-1 (VV, VH) and Sentinel-2 (B02-B12) patches with instruction text.
    """

    def __init__(
        self,
        dataset_dir: Optional[Path] = None,
        split: str = "train",
        task: Optional[str] = None,
        transform: Optional[Callable] = None,
        max_samples: Optional[int] = None,
        optical_bands: Optional[List[str]] = None,
        load_sar: bool = True,
    ):
        base_dir = dataset_dir or settings.data.bigearthnet_txt_dir
        super().__init__(base_dir, split=split, transform=transform, max_samples=max_samples)

        self.s2_dir = settings.data.sentinel2_dir
        self.s1_dir = settings.data.sentinel1_dir
        self.annotations_dir = settings.data.annotations_dir
        self.optical_bands = optical_bands or settings.model.optical_bands
        self.sar_polarizations = settings.model.sar_polarizations
        self.load_sar = load_sar
        self.task = task
        self.records: List[Dict[str, Any]] = []

        self._load_annotations()

    def _load_annotations(self) -> None:
        """Load BigEarthNet.txt parquet or benchmark JSON annotations."""
        parquet_file = self.annotations_dir / "BigEarthNet.txt.parquet"
        json_file = self.annotations_dir / "bigearthnet_txt_benchmark.json"

        loaded = False
        if parquet_file.exists():
            try:
                import pandas as pd
                df = pd.read_parquet(parquet_file)
                if "split" in df.columns and self.split != "all":
                    # If split exists and matches
                    filtered = df[df["split"] == self.split]
                    if len(filtered) > 0:
                        df = filtered
                self.records = df.to_dict(orient="records")
                loaded = True
                logger.info(f"Loaded {len(self.records)} records from {parquet_file}")
            except Exception as e:
                logger.warning(f"Could not read parquet with pandas ({e}). Checking json...")

        if not loaded and json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if self.split != "all":
                    filtered = [r for r in data if r.get("split") == self.split]
                    self.records = filtered if len(filtered) > 0 else data
                else:
                    self.records = data
                loaded = True
                logger.info(f"Loaded {len(self.records)} benchmark records from {json_file}")
            except Exception as e:
                logger.error(f"Failed to read json benchmark: {e}")

        # Filter by task category if requested
        if self.task and self.records:
            self.records = [
                r for r in self.records
                if self.task.lower() in str(r.get("type", "")).lower() or self.task.lower() in str(r.get("category", "")).lower()
            ]

        self.samples = self.records

    def _load_optical_patch(self, patch_id: str) -> np.ndarray:
        """
        Loads specified optical bands for a Sentinel-2 patch.
        Returns tensor of shape (C, H, W) normalized to [0, 1].
        """
        patch_dir = self.s2_dir / patch_id
        band_arrays = []

        for band in self.optical_bands:
            band_path = patch_dir / f"{patch_id}_{band}.tif"
            if band_path.exists():
                try:
                    img = Image.open(band_path)
                    arr = np.array(img, dtype=np.float32)
                    # Resize to 120x120 if 20m/60m band
                    if arr.shape != (120, 120):
                        pil_img = Image.fromarray(arr)
                        pil_img = pil_img.resize((120, 120), Image.BILINEAR)
                        arr = np.array(pil_img, dtype=np.float32)
                    band_arrays.append(arr)
                except Exception:
                    band_arrays.append(np.zeros((120, 120), dtype=np.float32))
            else:
                band_arrays.append(np.zeros((120, 120), dtype=np.float32))

        if not band_arrays:
            # Fallback mock 6-band tensor
            return np.zeros((len(self.optical_bands), 120, 120), dtype=np.float32)

        stack = np.stack(band_arrays, axis=0)
        # Normalize 16-bit reflectance (0-10000) to 0.0-1.0
        stack = np.clip(stack / 10000.0, 0.0, 1.0)
        return stack

    def _load_sar_patch(self, s1_name: Optional[str]) -> np.ndarray:
        """
        Loads VV and VH polarizations for a Sentinel-1 patch.
        Returns tensor of shape (2, H, W) in linear / normalized dB amplitude.
        """
        if not s1_name:
            return np.zeros((2, 120, 120), dtype=np.float32)

        patch_dir = self.s1_dir / s1_name
        pol_arrays = []

        for pol in self.sar_polarizations:
            pol_path = patch_dir / f"{s1_name}_{pol}.tif"
            if pol_path.exists():
                try:
                    img = Image.open(pol_path)
                    arr = np.array(img, dtype=np.float32)
                    if arr.shape != (120, 120):
                        pil_img = Image.fromarray(arr)
                        pil_img = pil_img.resize((120, 120), Image.BILINEAR)
                        arr = np.array(pil_img, dtype=np.float32)
                    pol_arrays.append(arr)
                except Exception:
                    pol_arrays.append(np.zeros((120, 120), dtype=np.float32))
            else:
                pol_arrays.append(np.zeros((120, 120), dtype=np.float32))

        if not pol_arrays:
            return np.zeros((2, 120, 120), dtype=np.float32)

        stack = np.stack(pol_arrays, axis=0)
        # Normalize SAR uint16 amplitude to 0.0-1.0
        stack = np.clip(stack / 65535.0, 0.0, 1.0)
        return stack

    def __getitem__(self, idx: int) -> TemporalVQASample:
        """
        Returns a TemporalVQASample mapped to the universal system interface.
        """
        record = self.records[idx] if self.records else {}

        patch_id = record.get("patch_id", "SAMPLE_S2")
        s1_name = record.get("s1_name", "SAMPLE_S1")
        prompt = record.get("input", "Describe the land cover.")
        target_output = record.get("output", "")
        task_category = record.get("category", "General")
        task_type = record.get("type", "vqa")

        optical_arr = self._load_optical_patch(patch_id)
        sar_arr = self._load_sar_patch(s1_name) if self.load_sar else None

        # RGB representation for legacy visualization (B04=Red, B03=Green, B02=Blue)
        if optical_arr.shape[0] >= 3:
            rgb_repr = (optical_arr[:3] * 255).astype(np.uint8).transpose(1, 2, 0)
        else:
            rgb_repr = (optical_arr[0:1].repeat(3, axis=0) * 255).astype(np.uint8).transpose(1, 2, 0)

        # Parse bounding box if referring expression task
        bboxes = None
        if task_type == "bounding box" or "[" in target_output:
            try:
                clean_str = target_output.replace("[", "").replace("]", "").strip()
                coords = [int(float(x.strip())) for x in clean_str.split(",")]
                if len(coords) == 4:
                    bboxes = [BoundingBox(y_min=coords[0], x_min=coords[1], y_max=coords[2], x_max=coords[3])]
            except Exception:
                pass

        return TemporalVQASample(
            sample_id=str(record.get("ID", f"BEN_{idx:06d}")),
            image_t1=rgb_repr,
            image_t2=sar_arr,  # Modality 2 is SAR (Mode A: cross-modal pair)
            question=prompt,
            answer=target_output,
            timestamp_t1="2017-06-13T10:10:31Z",
            timestamp_t2="2017-06-13T16:50:43Z",
            bbox_targets=bboxes,
            metadata={
                "patch_id_optical": patch_id,
                "patch_id_sar": s1_name,
                "dataset": "BigEarthNet.txt",
                "task_category": task_category,
                "task_type": task_type,
                "interpretation_mode": AnalysisInterpretationMode.MODE_A_CROSS_MODAL,
            }
        )

    def get_multimodal_sample(self, idx: int) -> BigEarthNetMultimodalSample:
        """
        Returns full typed BigEarthNetMultimodalSample with raw multi-band tensors.
        """
        record = self.records[idx] if self.records else {}
        patch_id = record.get("patch_id", "SAMPLE_S2")
        s1_name = record.get("s1_name", "SAMPLE_S1")

        optical_arr = self._load_optical_patch(patch_id)
        sar_arr = self._load_sar_patch(s1_name)

        return BigEarthNetMultimodalSample(
            sample_id=str(record.get("ID", f"BEN_{idx:06d}")),
            patch_id_optical=patch_id,
            patch_id_sar=s1_name,
            optical_image=optical_arr,
            sar_image=sar_arr,
            task_category=record.get("type", "vqa"),
            task_name=record.get("category", "Presence"),
            instruction=record.get("input"),
            question=record.get("input"),
            answer=record.get("output"),
            split=record.get("split", self.split),
            sensor_metadata=SensorObservationMetadata(
                optical_bands=self.optical_bands,
                optical_timestamp="2017-06-13T10:10:31Z",
                sar_polarizations=self.sar_polarizations,
                sar_timestamp="2017-06-13T16:50:43Z"
            ),
            metadata=record
        )
