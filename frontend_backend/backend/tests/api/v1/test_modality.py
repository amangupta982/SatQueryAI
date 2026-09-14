import pytest
from app.schemas.image import ImageModality
from app.services.modality import ModalityDetectionService

def test_detect_sar():
    # Via filename
    res = ModalityDetectionService.detect_modality({}, "S1A_IW_GRDH_1SDV_2019.tif")
    assert res.modality == ImageModality.SAR
    
    # Via metadata
    res = ModalityDetectionService.detect_modality({"raster_metadata": {"TIFFTAG_IMAGEDESCRIPTION": "VV polarization"}}, "image.tif")
    assert res.modality == ImageModality.SAR

def test_detect_multispectral():
    # Via filename
    res = ModalityDetectionService.detect_modality({}, "S2A_MSIL2A_2019.tif")
    assert res.modality == ImageModality.MULTISPECTRAL
    
    # Via band count
    res = ModalityDetectionService.detect_modality({"bands": 13}, "image.tif")
    assert res.modality == ImageModality.MULTISPECTRAL

def test_detect_optical():
    res = ModalityDetectionService.detect_modality({"bands": 3}, "image.tif")
    assert res.modality == ImageModality.OPTICAL
    
    res = ModalityDetectionService.detect_modality({"bands": 4}, "image.tif")
    assert res.modality == ImageModality.OPTICAL

def test_detect_unknown():
    res = ModalityDetectionService.detect_modality({"bands": 1}, "image.tif")
    assert res.modality == ImageModality.UNKNOWN
    
    res = ModalityDetectionService.detect_modality({}, "unknown_sensor.tif")
    assert res.modality == ImageModality.UNKNOWN
