import numpy as np
from app.schemas.preprocessing import OpticalPreprocessConfig
from app.services.preprocessing.base import BasePreprocessor

class OpticalPreprocessor(BasePreprocessor):
    def process(self, data: np.ndarray, config: OpticalPreprocessConfig) -> np.ndarray:
        """
        Process Optical data.
        data: shape (C, H, W)
        """
        # 1. Band Selection
        if config.bands_to_keep:
            data = self.select_bands(data, config.bands_to_keep)
            
        # Ensure float32 for processing
        data = data.astype(np.float32)
        
        # 2. Clipping
        if config.clip_percentile:
            # Clip outlier high values (e.g., clouds) across the spatial dims
            clip_val = np.percentile(data, config.clip_percentile)
            data = np.clip(data, a_min=None, a_max=clip_val)

        # 3. Min/Max Scaling
        if config.min_val is not None and config.max_val is not None:
            c = data.shape[0]
            # Handle scalar vs list/tuple for min/max
            if isinstance(config.min_val, (list, tuple)) and isinstance(config.max_val, (list, tuple)):
                if len(config.min_val) != c or len(config.max_val) != c:
                    raise ValueError(f"min_val/max_val length must match band count ({c})")
                
                min_arr = np.array(config.min_val).reshape(c, 1, 1)
                max_arr = np.array(config.max_val).reshape(c, 1, 1)
            else:
                min_arr = float(config.min_val)
                max_arr = float(config.max_val)
                
            # Avoid division by zero
            denom = max_arr - min_arr
            denom = np.where(denom == 0, 1e-8, denom)
            data = (data - min_arr) / denom

        # 4. Standard Scaling (Z-score)
        if config.mean is not None and config.std is not None:
            c = data.shape[0]
            if len(config.mean) != c or len(config.std) != c:
                raise ValueError(f"mean/std length must match band count ({c})")
            
            mean_arr = np.array(config.mean).reshape(c, 1, 1)
            std_arr = np.array(config.std).reshape(c, 1, 1)
            
            std_arr = np.where(std_arr == 0, 1e-8, std_arr)
            data = (data - mean_arr) / std_arr

        # 5. Spatial Cropping
        if config.crop:
            data = self.crop(data, config.crop)
            
        # 6. Spatial Resizing
        if config.resize:
            data = self.resize(data, config.resize)
            
        return data
