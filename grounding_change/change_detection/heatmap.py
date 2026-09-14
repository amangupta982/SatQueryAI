"""
Continuous Change Intensity Heatmap Generator.
Generates multi-scale continuous change representations:
- Raw temporal difference
- Normalized feature difference
- Learned change probability
- Semantic change probability
- Multi-scale fused change intensity
"""

from typing import Dict, Optional, Tuple
import cv2
import numpy as np


class ChangeHeatmapGenerator:
    """
    Constructs multi-level continuous change intensity heatmaps,
    distinguishing subtle continuous changes from significant semantic transitions.
    """

    @staticmethod
    def generate_heatmap(
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        learned_prob: Optional[np.ndarray] = None,
        feat_diff: Optional[np.ndarray] = None,
        semantic_prob_diff: Optional[np.ndarray] = None,
    ) -> Dict[str, np.ndarray]:
        """
        Produces multi-component change intensity maps in float32 [0.0, 1.0].
        """
        h, w = img_t1.shape[:2]

        # 1. Raw temporal RGB/grayscale difference
        if img_t1.ndim == 3 and img_t1.shape[-1] == 3:
            raw_diff = np.linalg.norm(img_t2.astype(np.float32) - img_t1.astype(np.float32), axis=-1) / np.sqrt(3.0)
        else:
            g1 = cv2.cvtColor(img_t1, cv2.COLOR_RGB2GRAY) if img_t1.ndim == 3 else img_t1
            g2 = cv2.cvtColor(img_t2, cv2.COLOR_RGB2GRAY) if img_t2.ndim == 3 else img_t2
            raw_diff = np.abs(g2.astype(np.float32) - g1.astype(np.float32))

        max_diff = np.max(raw_diff)
        if max_diff > 0:
            raw_diff_norm = raw_diff / max_diff
        else:
            raw_diff_norm = np.zeros_like(raw_diff)

        # 2. Learned change probability (from neural model)
        if learned_prob is not None:
            if learned_prob.shape[:2] != (h, w):
                learned_prob_norm = cv2.resize(learned_prob, (w, h))
            else:
                learned_prob_norm = learned_prob.astype(np.float32)
        else:
            learned_prob_norm = raw_diff_norm.copy()

        # 3. Feature difference score
        if feat_diff is not None:
            if feat_diff.shape[:2] != (h, w):
                feat_diff_norm = cv2.resize(feat_diff, (w, h))
            else:
                feat_diff_norm = feat_diff.astype(np.float32)
            f_max = np.max(feat_diff_norm)
            if f_max > 0:
                feat_diff_norm /= f_max
        else:
            feat_diff_norm = learned_prob_norm.copy()

        # 4. Semantic probability difference
        if semantic_prob_diff is not None:
            if semantic_prob_diff.shape[:2] != (h, w):
                sem_diff_norm = cv2.resize(semantic_prob_diff, (w, h))
            else:
                sem_diff_norm = semantic_prob_diff.astype(np.float32)
        else:
            sem_diff_norm = learned_prob_norm.copy()

        # 5. Composite Final Change Intensity Heatmap
        # Balanced combination: 50% neural learned change, 30% semantic transition, 20% visual feature difference
        composite_intensity = (
            0.50 * learned_prob_norm
            + 0.30 * sem_diff_norm
            + 0.20 * feat_diff_norm
        )
        composite_intensity = np.clip(composite_intensity, 0.0, 1.0)

        return {
            "raw_difference": raw_diff_norm,
            "feature_difference": feat_diff_norm,
            "learned_probability": learned_prob_norm,
            "semantic_probability": sem_diff_norm,
            "composite_heatmap": composite_intensity,
        }

    @staticmethod
    def render_color_heatmap(intensity_map: np.ndarray, colormap: int = cv2.COLORMAP_JET) -> np.ndarray:
        """
        Renders a continuous [0, 1] intensity map into an RGB color heatmap.
        """
        intensity_uint8 = (np.clip(intensity_map, 0.0, 1.0) * 255).astype(np.uint8)
        color_bgr = cv2.applyColorMap(intensity_uint8, colormap)
        color_rgb = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2RGB)
        return color_rgb
