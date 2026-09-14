import pytest
import numpy as np
from app.schemas.preprocessing import OpticalPreprocessConfig, SARPreprocessConfig, CropConfig, ResizeConfig
from app.services.preprocessing.optical import OpticalPreprocessor
from app.services.preprocessing.sar import SARPreprocessor
from app.services.preprocessing.tensor import RasterTensorConverter

def test_optical_preprocessor():
    # 2 bands, 10x10
    data = np.ones((2, 10, 10)) * 5000.0
    
    config = OpticalPreprocessConfig(
        min_val=[0.0, 0.0],
        max_val=[10000.0, 10000.0],
        crop=CropConfig(crop_type="center", size=(4, 4)),
        resize=ResizeConfig(target_size=(8, 8))
    )
    
    preprocessor = OpticalPreprocessor()
    out = preprocessor.process(data, config)
    
    # 5000 normalized 0-10000 should be 0.5
    assert np.allclose(out, 0.5)
    
    # After cropping to 4x4 and resizing to 8x8, shape should be (2, 8, 8)
    assert out.shape == (2, 8, 8)

def test_optical_standard_scaler():
    # 1 band, 10x10
    data = np.ones((1, 10, 10)) * 100.0
    
    config = OpticalPreprocessConfig(
        mean=[100.0],
        std=[10.0]
    )
    
    preprocessor = OpticalPreprocessor()
    out = preprocessor.process(data, config)
    
    # (100 - 100) / 10 = 0.0
    assert np.allclose(out, 0.0)

def test_sar_preprocessor():
    # 1 band, 10x10 amplitude data
    data = np.ones((1, 10, 10)) * 0.1 # 0.1 amplitude -> 10*log10(0.1) = -10 dB
    
    config = SARPreprocessConfig(
        to_db=True,
        db_min=-25.0,
        db_max=0.0
    )
    
    preprocessor = SARPreprocessor()
    out = preprocessor.process(data, config)
    
    # -10 dB normalized to [-25, 0] is (-10 - -25) / 25 = 15 / 25 = 0.6
    assert np.allclose(out, 0.6)
    
def test_tensor_conversion():
    data = np.zeros((3, 10, 10))
    converter = RasterTensorConverter()
    
    # default channel first
    t1 = converter.to_tensor(data)
    assert t1.shape == (3, 10, 10)
    assert t1.dtype == np.float32
    
    # channel last
    t2 = converter.to_tensor(data, channel_first=False)
    assert t2.shape == (10, 10, 3)
