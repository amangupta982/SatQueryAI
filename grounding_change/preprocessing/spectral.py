"""
Multispectral Analysis and Remote-Sensing Index Calculator.
Calculates NDVI, NDWI, NDBI when spectral bands are available.
Never computes an index without the required bands.
"""

from typing import Any, Dict, Optional, Tuple
import numpy as np
from ..schemas import SpectralIndexStats


class SpectralIndexAnalyzer:
    """
    Computes standard remote-sensing vegetation, water, and built-up indices
    as physical evidence for detected temporal changes.
    """

    @staticmethod
    def calculate_normalized_diff(band_a: np.ndarray, band_b: np.ndarray) -> np.ndarray:
        """Normalized difference (A - B) / (A + B). Returns values in [-1.0, 1.0]."""
        denom = band_a.astype(np.float32) + band_b.astype(np.float32)
        diff = band_a.astype(np.float32) - band_b.astype(np.float32)
        with np.errstate(divide='ignore', invalid='ignore'):
            result = np.where(denom != 0, diff / denom, 0.0)
        return np.clip(result, -1.0, 1.0)

    @classmethod
    def compute_all_indices(
        cls,
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        band_mapping: Optional[Dict[str, int]] = None
    ) -> Dict[str, SpectralIndexStats]:
        """
        Calculates available spectral indices across T1 and T2.

        band_mapping: optional dictionary e.g. {'red': 0, 'green': 1, 'blue': 2, 'nir': 3, 'swir': 4}
        If band count is 3 (RGB only), spectral indices needing NIR/SWIR report available=False.
        """
        results: Dict[str, SpectralIndexStats] = {
            "NDVI": SpectralIndexStats(available=False),
            "NDWI": SpectralIndexStats(available=False),
            "NDBI": SpectralIndexStats(available=False),
        }

        # Check channel count
        c1 = img_t1.shape[0] if img_t1.ndim == 3 and img_t1.shape[0] < img_t1.shape[2] else (img_t1.shape[-1] if img_t1.ndim == 3 else 1)
        c2 = img_t2.shape[0] if img_t2.ndim == 3 and img_t2.shape[0] < img_t2.shape[2] else (img_t2.shape[-1] if img_t2.ndim == 3 else 1)

        num_bands = min(c1, c2)

        # Standard 4+ band imagery (Blue, Green, Red, NIR, ...)
        has_nir = False
        has_swir = False
        red_idx, green_idx, nir_idx, swir_idx = 2, 1, 3, 4

        if band_mapping:
            red_idx = band_mapping.get("red", 2)
            green_idx = band_mapping.get("green", 1)
            nir_idx = band_mapping.get("nir", 3)
            swir_idx = band_mapping.get("swir", 4)
            has_nir = "nir" in band_mapping and band_mapping["nir"] < num_bands
            has_swir = "swir" in band_mapping and band_mapping["swir"] < num_bands
        else:
            if num_bands >= 4:
                has_nir = True
            if num_bands >= 5:
                has_swir = True

        def get_band(img: np.ndarray, idx: int) -> np.ndarray:
            if img.shape[0] == num_bands:
                return img[idx]
            return img[..., idx]

        # 1. NDVI (Normalized Difference Vegetation Index): (NIR - Red) / (NIR + Red)
        if has_nir and red_idx < num_bands and nir_idx < num_bands:
            t1_ndvi = cls.calculate_normalized_diff(get_band(img_t1, nir_idx), get_band(img_t1, red_idx))
            t2_ndvi = cls.calculate_normalized_diff(get_band(img_t2, nir_idx), get_band(img_t2, red_idx))
            m1, m2 = float(np.mean(t1_ndvi)), float(np.mean(t2_ndvi))
            results["NDVI"] = SpectralIndexStats(
                available=True,
                t1_mean=round(m1, 4),
                t2_mean=round(m2, 4),
                change=round(m2 - m1, 4)
            )

        # 2. NDWI (Normalized Difference Water Index): (Green - NIR) / (Green + NIR)
        if has_nir and green_idx < num_bands and nir_idx < num_bands:
            t1_ndwi = cls.calculate_normalized_diff(get_band(img_t1, green_idx), get_band(img_t1, nir_idx))
            t2_ndwi = cls.calculate_normalized_diff(get_band(img_t2, green_idx), get_band(img_t2, nir_idx))
            m1, m2 = float(np.mean(t1_ndwi)), float(np.mean(t2_ndwi))
            results["NDWI"] = SpectralIndexStats(
                available=True,
                t1_mean=round(m1, 4),
                t2_mean=round(m2, 4),
                change=round(m2 - m1, 4)
            )

        # 3. NDBI (Normalized Difference Built-up Index): (SWIR - NIR) / (SWIR + NIR)
        if has_swir and nir_idx < num_bands and swir_idx < num_bands:
            t1_ndbi = cls.calculate_normalized_diff(get_band(img_t1, swir_idx), get_band(img_t1, nir_idx))
            t2_ndbi = cls.calculate_normalized_diff(get_band(img_t2, swir_idx), get_band(img_t2, nir_idx))
            m1, m2 = float(np.mean(t1_ndbi)), float(np.mean(t2_ndbi))
            results["NDBI"] = SpectralIndexStats(
                available=True,
                t1_mean=round(m1, 4),
                t2_mean=round(m2, 4),
                change=round(m2 - m1, 4)
            )

        return results
