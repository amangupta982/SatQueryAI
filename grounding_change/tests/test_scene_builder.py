"""
Unit Tests for Scene Builder, Region Extraction, and Change Statistics.
"""

import numpy as np
import pytest

from grounding_change.grounding.region_extractor import RegionExtractor, encode_rle, decode_rle
from grounding_change.change_detection.statistics import ChangeStatisticsCalculator
from grounding_change.change_detection.scene_builder import TemporalSceneBuilder
from grounding_change.taxonomy import taxonomy


def test_rle_encode_decode():
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[10:20, 10:20] = 1
    rle = encode_rle(mask)
    assert isinstance(rle, str)
    decoded = decode_rle(rle, (32, 32))
    np.testing.assert_array_equal(mask, decoded)


def test_region_extractor():
    extractor = RegionExtractor(min_area_pixels=10)
    change_mask = np.zeros((100, 100), dtype=np.uint8)
    change_mask[10:30, 10:30] = 1  # 400 pixels (Region 1)
    change_mask[60:75, 60:80] = 1  # 300 pixels (Region 2)

    sem_t1 = np.full((100, 100), 5, dtype=np.int64)  # bare_land
    sem_t2 = np.full((100, 100), 1, dtype=np.int64)  # building

    regions = extractor.extract_regions(change_mask, sem_t1, sem_t2)
    assert len(regions) == 2
    assert regions[0].area_pixels == 400
    assert regions[0].category == "building"
    assert regions[0].change_type == "added"
    assert regions[0].bbox == [10, 10, 30, 30]


def test_statistics_calculator():
    sem_t1 = np.zeros((100, 100), dtype=np.int64)
    sem_t1[:50, :] = 2  # vegetation 50%
    sem_t1[50:, :] = 5  # bare_land 50%

    sem_t2 = sem_t1.copy()
    sem_t2[20:40, 20:40] = 1  # building added on vegetation (400 px = 4%)

    change_mask = (sem_t1 != sem_t2).astype(np.uint8)

    extractor = RegionExtractor(min_area_pixels=5)
    regions = extractor.extract_regions(change_mask, sem_t1, sem_t2)

    calc = ChangeStatisticsCalculator()
    cat_stats = calc.compute_category_statistics(sem_t1, sem_t2, change_mask, regions)
    assert "building" in cat_stats
    assert cat_stats["building"].change_percent == 4.0
    assert cat_stats["building"].direction == "increase"

    transitions = calc.compute_transitions(sem_t1, sem_t2, change_mask)
    assert len(transitions) == 1
    assert transitions[0].from_category == "vegetation"
    assert transitions[0].to_category == "building"
    assert transitions[0].pixel_count == 400


def test_zero_question_scene_builder():
    builder = TemporalSceneBuilder()
    img_t1 = np.full((100, 100, 3), 120, dtype=np.uint8)
    img_t2 = img_t1.copy()

    change_probs = np.zeros((100, 100), dtype=np.float32)
    change_probs[20:40, 20:40] = 0.9  # Region of change

    sem_t1 = np.full((100, 100), 2, dtype=np.int64)  # vegetation
    sem_t2 = np.full((100, 100), 2, dtype=np.int64)
    sem_t2[20:40, 20:40] = 1  # building

    scene = builder.build_scene(img_t1, img_t2, change_probs, sem_t1, sem_t2)

    assert scene.summary.change_detected is True
    assert scene.summary.changed_pixels == 400
    assert len(scene.regions) == 1
    assert scene.regions[0].category == "building"
    assert "building" in scene.categories
    assert scene.summary.natural_language_summary != ""
