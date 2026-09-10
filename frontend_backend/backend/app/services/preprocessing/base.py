from abc import ABC, abstractmethod
import numpy as np
import cv2
import random
from typing import List, Tuple
from app.schemas.preprocessing import CropConfig, ResizeConfig

class BasePreprocessor(ABC):
    @abstractmethod
    def process(self, data: np.ndarray, config) -> np.ndarray:
        """
        Process the data (C, H, W) through the pipeline.
        Must be implemented by subclasses.
        """
        pass

    def select_bands(self, data: np.ndarray, bands_to_keep: List[int]) -> np.ndarray:
        """
        data: shape (C, H, W)
        """
        if not bands_to_keep:
            return data
        # Validate bands
        max_idx = data.shape[0] - 1
        for b in bands_to_keep:
            if b < 0 or b > max_idx:
                raise ValueError(f"Band index {b} is out of bounds for data with {data.shape[0]} bands.")
        return data[bands_to_keep, :, :]

    def resize(self, data: np.ndarray, config: ResizeConfig) -> np.ndarray:
        """
        Resizes the data to target_size (H, W).
        Input data: (C, H, W).
        Output data: (C, target_H, target_W).
        """
        # cv2 expects (H, W, C)
        # transpose (C, H, W) -> (H, W, C)
        hwc = np.transpose(data, (1, 2, 0))
        
        interp_map = {
            "nearest": cv2.INTER_NEAREST,
            "bilinear": cv2.INTER_LINEAR,
            "bicubic": cv2.INTER_CUBIC
        }
        interp = interp_map.get(config.interpolation.lower(), cv2.INTER_LINEAR)
        
        target_h, target_w = config.target_size
        # cv2.resize takes dsize as (width, height)
        resized = cv2.resize(hwc, (target_w, target_h), interpolation=interp)
        
        # If output is 2D (single channel), cv2 drops the channel dim. Add it back.
        if len(resized.shape) == 2:
            resized = np.expand_dims(resized, axis=-1)
            
        # transpose back to (C, H, W)
        return np.transpose(resized, (2, 0, 1))

    def crop(self, data: np.ndarray, config: CropConfig) -> np.ndarray:
        """
        Crops data (C, H, W).
        """
        _, h, w = data.shape
        target_h, target_w = config.size
        
        if target_h > h or target_w > w:
            raise ValueError(f"Crop size {config.size} is larger than image size ({h}, {w}).")
            
        if config.crop_type == "center":
            y = (h - target_h) // 2
            x = (w - target_w) // 2
        elif config.crop_type == "random":
            y = random.randint(0, h - target_h)
            x = random.randint(0, w - target_w)
        else:
            raise ValueError(f"Unknown crop type {config.crop_type}")
            
        return data[:, y:y+target_h, x:x+target_w]
