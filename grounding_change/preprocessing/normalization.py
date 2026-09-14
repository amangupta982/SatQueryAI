"""
Radiometric Normalization & Illumination Correction.
Mitigates false changes caused by differing sun angles, seasonal solar irradiance,
atmospheric haze, and transient sensor gains.
"""

from typing import Tuple, Union
import numpy as np
from skimage.exposure import match_histograms


class RadiometricNormalizer:
    """
    Normalizes temporal imagery to harmonize atmospheric and illumination conditions.
    """

    @staticmethod
    def match_temporal_histograms(
        img_t1: np.ndarray,
        img_t2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Harmonizes atmospheric and illumination conditions between T1 and T2
        using channel-wise linear radiometric adjustment (gain and offset).
        Preserves local contrast and real physical changes, unlike naive full CDF matching.
        """
        t1_f = img_t1.astype(np.float32)
        t2_f = img_t2.astype(np.float32)

        matched_t2 = np.zeros_like(t2_f)
        channels = t1_f.shape[-1] if t1_f.ndim == 3 else 1

        for c in range(channels):
            c1 = t1_f[..., c] if channels > 1 else t1_f
            c2 = t2_f[..., c] if channels > 1 else t2_f

            m1, s1 = float(np.mean(c1)), float(np.std(c1))
            m2, s2 = float(np.mean(c2)), float(np.std(c2))

            if s2 > 1e-4:
                gain = float(np.clip(s1 / s2, 0.75, 1.35))
                offset = m1 - gain * m2
                adjusted = gain * c2 + offset
            else:
                adjusted = c2

            if channels > 1:
                matched_t2[..., c] = adjusted
            else:
                matched_t2 = adjusted

        matched_t2 = np.clip(matched_t2, 0, 255).astype(img_t2.dtype)
        return img_t1, matched_t2

    @staticmethod
    def percentile_rescale(
        img: np.ndarray,
        p_low: float = 2.0,
        p_high: float = 98.0
    ) -> np.ndarray:
        """
        Adaptive contrast stretching between p_low and p_high percentiles.
        Normalizes outputs to float [0, 1].
        """
        img_f = img.astype(np.float32)
        v_min = np.percentile(img_f, p_low)
        v_max = np.percentile(img_f, p_high)

        if v_max > v_min:
            rescaled = np.clip((img_f - v_min) / (v_max - v_min), 0.0, 1.0)
        else:
            rescaled = np.zeros_like(img_f)
        return rescaled

    @staticmethod
    def suppress_shadow_artifacts(
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        shadow_thresh: float = 0.15
    ) -> np.ndarray:
        """
        Identifies deep shadow regions that can produce false building or vegetation changes.
        Returns a boolean mask where changes are deemed low-reliability due to extreme shadows.
        """
        gray1 = np.mean(img_t1, axis=-1) if img_t1.ndim == 3 else img_t1
        gray2 = np.mean(img_t2, axis=-1) if img_t2.ndim == 3 else img_t2

        max_val = max(gray1.max(), gray2.max(), 1.0)
        shadow1 = (gray1 / max_val) < shadow_thresh
        shadow2 = (gray2 / max_val) < shadow_thresh

        # Areas where shadow appeared or disappeared
        shadow_differential = shadow1 ^ shadow2
        return shadow_differential
