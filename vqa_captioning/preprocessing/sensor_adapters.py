"""
Sensor preprocessing adapters for Sentinel-2 Optical and Sentinel-1 SAR imagery.
Ensures correct radiometric calibration, band selection, normalization,
and false-color / composite creation for Vision-Language Models.
"""

import os
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from PIL import Image

class Sentinel2Adapter:
    """
    Adapter for Sentinel-2 MSI (Multispectral Instrument).
    12 bands:
      10m: B02 (Blue), B03 (Green), B04 (Red), B08 (NIR)
      20m: B05, B06, B07 (Red Edge), B8A (Narrow NIR), B11, B12 (SWIR)
      60m: B01 (Coastal Aerosol), B09 (Water Vapour)
    """

    BAND_ORDER_12 = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"]
    RGB_INDICES = [3, 2, 1]  # B04 (Red), B03 (Green), B02 (Blue) in 12-band array

    @staticmethod
    def normalize_band(band_data: np.ndarray, lower_pct: float = 2.0, upper_pct: float = 98.0) -> np.ndarray:
        """
        Robust percentile normalization of a reflectance band to [0, 255] uint8.
        Sentinel-2 L2A/L1C surface reflectance is typically scaled by 10,000.
        """
        band_float = band_data.astype(np.float32)
        valid_mask = ~np.isnan(band_float)
        if not np.any(valid_mask):
            return np.zeros_like(band_data, dtype=np.uint8)

        # Remove negative or extreme outliers
        p_low = np.percentile(band_float[valid_mask], lower_pct)
        p_high = np.percentile(band_float[valid_mask], upper_pct)

        if p_high <= p_low:
            p_high = p_low + 1.0

        clipped = np.clip(band_float, p_low, p_high)
        normalized = ((clipped - p_low) / (p_high - p_low) * 255.0).astype(np.uint8)
        return normalized

    @classmethod
    def create_rgb_composite(cls, multi_band_array: np.ndarray, band_names: Optional[List[str]] = None) -> Image.Image:
        """
        Create a calibrated RGB PIL Image from a multi-band numpy array.
        Handles shape (Bands, Height, Width) or (Height, Width, Bands).
        """
        arr = multi_band_array
        if arr.ndim == 2:
            # Grayscale single band
            norm = cls.normalize_band(arr)
            return Image.fromarray(norm, mode="L").convert("RGB")

        if arr.shape[0] in [12, 10, 4, 3] and arr.shape[0] < arr.shape[1]:
            # (Channels, Height, Width) -> transpose to (H, W, C)
            arr = np.transpose(arr, (1, 2, 0))

        h, w, c = arr.shape
        if c == 3:
            # Standard 3-channel input
            r = cls.normalize_band(arr[:, :, 0])
            g = cls.normalize_band(arr[:, :, 1])
            b = cls.normalize_band(arr[:, :, 2])
        elif c >= 4:
            # Multispectral: extract Red, Green, Blue
            # Default Sentinel-2 BigEarthNet: B04 (Red)=idx 3, B03 (Green)=idx 2, B02 (Blue)=idx 1
            if band_names:
                r_idx = band_names.index("B04") if "B04" in band_names else 0
                g_idx = band_names.index("B03") if "B03" in band_names else 1
                b_idx = band_names.index("B02") if "B02" in band_names else 2
            else:
                r_idx, g_idx, b_idx = 3, 2, 1
            r = cls.normalize_band(arr[:, :, r_idx])
            g = cls.normalize_band(arr[:, :, g_idx])
            b = cls.normalize_band(arr[:, :, b_idx])
        else:
            raise ValueError(f"Unsupported channel dimension for RGB creation: {c}")

        rgb_stack = np.stack([r, g, b], axis=-1)
        return Image.fromarray(rgb_stack, mode="RGB")

    @classmethod
    def load_image(cls, image_path: str) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Load an optical image file (PNG/JPEG/TIFF/NPY) and return an RGB PIL Image + metadata.
        """
        metadata = {"source_path": image_path, "sensor": "Sentinel-2"}
        if image_path.endswith(".npy"):
            data = np.load(image_path)
            metadata["original_shape"] = list(data.shape)
            img = cls.create_rgb_composite(data)
            return img, metadata

        # Standard PIL load
        with Image.open(image_path) as raw:
            rgb = raw.convert("RGB")
            metadata["original_size"] = raw.size
            return rgb, metadata


class Sentinel1SARAdapter:
    """
    Adapter for Sentinel-1 Synthetic Aperture Radar (SAR).
    C-band dual polarization:
      VV (vertical transmit / vertical receive)
      VH (vertical transmit / horizontal receive)
    """

    @staticmethod
    def linear_to_db(backscatter_linear: np.ndarray) -> np.ndarray:
        """Convert linear amplitude/intensity to decibels: 10 * log10(x + eps)."""
        eps = 1e-7
        pos = np.maximum(backscatter_linear, eps)
        return 10.0 * np.log10(pos)

    @classmethod
    def normalize_sar_channel(cls, channel_data: np.ndarray, vmin: float = -25.0, vmax: float = 0.0) -> np.ndarray:
        """
        Normalize SAR backscatter in dB to [0, 255] uint8.
        Typical land backscatter ranges from -25 dB (quiet water) to 0 dB (urban structures).
        """
        data = channel_data.astype(np.float32)
        if np.max(data) > 1.0 and np.min(data) >= 0.0 and np.median(data) > 5.0:
            # Data is in linear or DN scale, convert to dB
            data = cls.linear_to_db(data)

        clipped = np.clip(data, vmin, vmax)
        normalized = ((clipped - vmin) / (vmax - vmin) * 255.0).astype(np.uint8)
        return normalized

    @classmethod
    def create_sar_composite(cls, vv_channel: np.ndarray, vh_channel: np.ndarray) -> Image.Image:
        """
        Create a standard 3-channel SAR false-color composite:
          Red: VV normalized
          Green: VH normalized
          Blue: Difference / Ratio (VV - VH in dB)
        """
        r = cls.normalize_sar_channel(vv_channel, vmin=-22.0, vmax=0.0)
        g = cls.normalize_sar_channel(vh_channel, vmin=-28.0, vmax=-5.0)

        # Cross-polarization ratio / difference
        diff = vv_channel.astype(np.float32) - vh_channel.astype(np.float32)
        b = cls.normalize_sar_channel(diff, vmin=0.0, vmax=15.0)

        stack = np.stack([r, g, b], axis=-1)
        return Image.fromarray(stack, mode="RGB")

    @classmethod
    def load_sar_image(cls, sar_path: str) -> Tuple[Image.Image, Dict[str, Any]]:
        """Load SAR imagery and produce a false-color composite for vision encoders."""
        metadata = {"source_path": sar_path, "sensor": "Sentinel-1"}
        if sar_path.endswith(".npy"):
            data = np.load(sar_path)
            metadata["original_shape"] = list(data.shape)
            if data.shape[0] >= 2:
                vv, vh = data[0], data[1]
            elif data.shape[-1] >= 2:
                vv, vh = data[:, :, 0], data[:, :, 1]
            else:
                vv = vh = data.squeeze()
            composite = cls.create_sar_composite(vv, vh)
            return composite, metadata

        with Image.open(sar_path) as raw:
            rgb = raw.convert("RGB")
            metadata["original_size"] = raw.size
            return rgb, metadata
