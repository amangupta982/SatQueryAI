import numpy as np
from typing import Protocol

class OpticalSARModel(Protocol):
    def predict(self, optical_tensor: np.ndarray, sar_tensor: np.ndarray, question: str) -> str:
        ...

class MockOpticalSARModel:
    def predict(self, optical_tensor: np.ndarray, sar_tensor: np.ndarray, question: str) -> str:
        """
        A mock multimodal model that acknowledges both distinct inputs without blindly concatenating them.
        """
        # Validate inputs are distinctly typed (e.g., Optical typically has multiple bands, SAR might have 1 or 2)
        opt_bands = optical_tensor.shape[0]
        sar_bands = sar_tensor.shape[0]
        
        return f"Based on the {opt_bands}-band optical data and {sar_bands}-band SAR backscatter, the structures visible in the optical data are confirmed by the SAR amplitude in response to: '{question}'"
