import numpy as np
from app.schemas.preprocessing import SARPreprocessConfig
from app.services.preprocessing.base import BasePreprocessor

class SARPreprocessor(BasePreprocessor):
    def process(self, data: np.ndarray, config: SARPreprocessConfig) -> np.ndarray:
        """
        Process SAR data.
        data: shape (C, H, W)
        """
        # 1. Band Selection
        if config.bands_to_keep:
            data = self.select_bands(data, config.bands_to_keep)
            
        data = data.astype(np.float32)

        # 2. Convert to Decibels
        if config.to_db:
            # Handle zeros or negative values (which shouldn't technically exist in raw amplitude, but can be artifacts)
            # Add a small epsilon to avoid log(0)
            epsilon = 1e-10
            data = np.where(data <= 0, epsilon, data)
            data = 10.0 * np.log10(data)
            
        # 3. Clip Min/Max (e.g. -25 to 0 dB)
        data = np.clip(data, a_min=config.db_min, a_max=config.db_max)

        # 4. Normalize to [0, 1] range for ML
        # Assuming db_min != db_max
        denom = config.db_max - config.db_min
        if denom == 0:
            denom = 1e-8
        data = (data - config.db_min) / denom
        
        # 5. Spatial Cropping
        if config.crop:
            data = self.crop(data, config.crop)
            
        # 6. Spatial Resizing
        if config.resize:
            data = self.resize(data, config.resize)
            
        return data
