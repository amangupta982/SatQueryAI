import numpy as np

class RasterTensorConverter:
    @staticmethod
    def to_tensor(data: np.ndarray, channel_first: bool = True) -> np.ndarray:
        """
        Converts generic rasterio numpy array to a standardized float32 ML tensor.
        Rasterio native format is usually (C, H, W).
        If channel_first is False, returns (H, W, C).
        """
        data = data.astype(np.float32)
        
        # Assume input is (C, H, W) based on Rasterio defaults and our Preprocessors
        if len(data.shape) == 2:
            # (H, W) -> (1, H, W)
            data = np.expand_dims(data, axis=0)
            
        if not channel_first:
            # (C, H, W) -> (H, W, C)
            data = np.transpose(data, (1, 2, 0))
            
        return data
