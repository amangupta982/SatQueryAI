import numpy as np
from typing import Protocol

class ChangeDetectionModel(Protocol):
    def detect_change(self, before_tensor: np.ndarray, after_tensor: np.ndarray) -> np.ndarray:
        ...

class BaselineChangeModel:
    def __init__(self, threshold: float = 0.2):
        self.threshold = threshold

    def detect_change(self, before_tensor: np.ndarray, after_tensor: np.ndarray) -> np.ndarray:
        """
        Implements Baseline Change Vector Analysis (CVA).
        Assumes tensors are shaped (C, H, W) and normalized to [0, 1].
        Returns a binary mask of shape (H, W).
        """
        # Ensure identical shapes
        if before_tensor.shape != after_tensor.shape:
            raise ValueError(f"Shape mismatch: {before_tensor.shape} vs {after_tensor.shape}")

        # Calculate absolute difference
        abs_diff = np.abs(after_tensor - before_tensor)
        
        # Average the difference across all bands
        # (C, H, W) -> (H, W)
        mean_diff = np.mean(abs_diff, axis=0)
        
        # Threshold the difference to create a binary mask (1 for change, 0 for no change)
        mask = np.where(mean_diff > self.threshold, 1, 0).astype(np.uint8)
        
        return mask
