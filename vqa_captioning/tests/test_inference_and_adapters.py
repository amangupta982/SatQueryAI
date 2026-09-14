"""
Tests for SatQueryPredictor, CountEvidenceAdapter, LandCoverEvidenceAdapter, and EvidenceExtractor.
"""

import numpy as np
import pytest
from PIL import Image

from vqa_captioning.inference.predictor import SatQueryPredictor
from vqa_captioning.inference.adapters import CountEvidenceAdapter, LandCoverEvidenceAdapter, AreaCalculator
from vqa_captioning.inference.evidence_extractor import EvidenceExtractor

def test_satquery_predictor_ask_schema():
    predictor = SatQueryPredictor(mock_mode=True)
    img = Image.new("RGB", (120, 120), color=(50, 100, 150))
    res = predictor.ask(image=img, question="Is water present?")

    assert "answer" in res
    assert "confidence" in res
    assert "task" in res
    assert "evidence" in res
    assert res["model"] == "SatQuery-VQA"
    assert res["task"] == "presence"

def test_count_evidence_adapter_limitation_handling():
    adapter = CountEvidenceAdapter()
    res = adapter.handle_count_query(
        image_input=None,
        question="How many buildings are in the scene?",
        vqa_model_fn=lambda img, q, task: {"answer": "18"},
    )

    assert "does not provide individual building" in res["answer"]
    assert res["confidence"] is None
    assert "grounding_change" in res["evidence"]["recommended_module"]

def test_count_evidence_adapter_with_external_detector():
    def mock_detector(img, q):
        return {
            "answer": "Detected 4 buildings using high-resolution detector.",
            "confidence": 0.94,
            "task": "count",
            "evidence": {"bounding_boxes": [[0.1, 0.1, 0.3, 0.3]]},
            "model": "GroundingDINO",
        }

    adapter = CountEvidenceAdapter(external_detector_fn=mock_detector)
    res = adapter.handle_count_query(None, "How many buildings?", None)
    assert "Detected 4 buildings" in res["answer"]
    assert res["confidence"] == 0.94

def test_area_calculator_pixel_count():
    # 100x100 mask with 2500 pixels set to 1 (25% coverage)
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[:50, :50] = 1

    stats = AreaCalculator.calculate_mask_area(mask, gsd_meters=10.0)
    assert stats["pixel_count"] == 2500
    assert stats["percentage"] == 25.0
    assert stats["area_m2"] == 2500 * 100.0  # 250,000 m2
    assert stats["area_km2"] == 0.25

def test_evidence_extractor_bounding_boxes_and_tiers():
    text = "The target is primary (>25% image coverage) located at [200, 300, 600, 700]."
    boxes = EvidenceExtractor.extract_bounding_boxes(text)
    tier = EvidenceExtractor.extract_coverage_tier(text)

    assert len(boxes) == 1
    assert boxes[0] == [0.2, 0.3, 0.6, 0.7]
    assert "Primary" in tier
