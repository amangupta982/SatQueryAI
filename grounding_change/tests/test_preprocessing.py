"""
Unit Tests for Temporal Preprocessing & Alignment.
"""

import numpy as np
import pytest

from grounding_change.preprocessing.alignment import TemporalAligner
from grounding_change.preprocessing.normalization import RadiometricNormalizer
from grounding_change.preprocessing.tiling import LargeRasterTiler
from grounding_change.preprocessing.spectral import SpectralIndexAnalyzer


def test_temporal_alignment():
    aligner = TemporalAligner()
    t1 = np.zeros((128, 128, 3), dtype=np.uint8)
    t1[40:80, 40:80] = [200, 200, 200]
    t2 = t1.copy()

    aligned, matrix, success = aligner.align(t1, t2)
    assert aligned.shape == t1.shape
    assert isinstance(success, bool)


def test_radiometric_normalization():
    normalizer = RadiometricNormalizer()
    t1 = np.random.randint(50, 150, (100, 100, 3), dtype=np.uint8)
    t2 = np.random.randint(100, 200, (100, 100, 3), dtype=np.uint8)

    _, matched_t2 = normalizer.match_temporal_histograms(t1, t2)
    assert matched_t2.shape == t2.shape

    rescaled = normalizer.percentile_rescale(t1)
    assert rescaled.min() >= 0.0
    assert rescaled.max() <= 1.0


def test_raster_tiling_and_stitching():
    tiler = LargeRasterTiler(tile_size=64, overlap=16)
    h, w = 150, 150
    coords = tiler.generate_tile_coords(h, w)
    assert len(coords) > 1

    tile_preds = []
    for (ymin, xmin, ymax, xmax) in coords:
        tile_preds.append(np.ones((ymax - ymin, xmax - xmin), dtype=np.float32) * 5.0)

    stitched = tiler.stitch_predictions(h, w, coords, tile_preds)
    assert stitched.shape == (h, w)
    np.testing.assert_allclose(stitched, 5.0, rtol=1e-3)


def test_spectral_indices():
    # 3-band RGB image (NIR not present)
    t1_rgb = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    t2_rgb = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    res_rgb = SpectralIndexAnalyzer.compute_all_indices(t1_rgb, t2_rgb)
    assert res_rgb["NDVI"].available is False
    assert res_rgb["NDWI"].available is False

    # 4-band Multispectral image (B, G, R, NIR)
    t1_ms = np.random.randint(0, 255, (64, 64, 4), dtype=np.uint8)
    t2_ms = np.random.randint(0, 255, (64, 64, 4), dtype=np.uint8)
    res_ms = SpectralIndexAnalyzer.compute_all_indices(t1_ms, t2_ms)
    assert res_ms["NDVI"].available is True
    assert res_ms["NDWI"].available is True
