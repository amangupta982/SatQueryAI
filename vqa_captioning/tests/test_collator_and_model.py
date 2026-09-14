"""
Tests for MultimodalDataCollator, MultiSensorProjector, and SatQueryVQA model wrapper.
"""

import torch
import pytest
from PIL import Image

from vqa_captioning.training.collator import MultimodalDataCollator, VQADataset
from vqa_captioning.models.multisensor_projector import MultiSensorProjector
from vqa_captioning.models.satquery_vqa_model import SatQueryVQA
from common.schemas.vqa import UnifiedVQASample

def test_multimodal_collator_tensor_shapes():
    samples = [
        UnifiedVQASample(
            sample_id="test_1",
            patch_id="p1",
            image_path="",
            question="Is water present?",
            answer="Yes",
            task="presence",
        ),
        UnifiedVQASample(
            sample_id="test_2",
            patch_id="p2",
            image_path="",
            question="What is the dominant land cover?",
            answer="Broad-leaved forest",
            task="size",
        ),
    ]

    collator = MultimodalDataCollator(processor=None, mock_mode=True)
    batch = collator(samples)

    assert "input_ids" in batch
    assert "attention_mask" in batch
    assert "labels" in batch
    assert batch["input_ids"].shape[0] == 2
    assert batch["attention_mask"].shape == batch["input_ids"].shape
    assert batch["labels"].shape == batch["input_ids"].shape

def test_multisensor_projector_forward():
    # s2_features: (batch=2, patches=16, dim=768)
    # s1_features: (batch=2, patches=16, dim=768)
    s2 = torch.randn(2, 16, 768)
    s1 = torch.randn(2, 16, 768)

    projector = MultiSensorProjector(s2_input_dim=768, s1_input_dim=768, llm_hidden_dim=2048)
    s2_tokens, s1_tokens = projector(s2_features=s2, s1_features=s1)

    assert s2_tokens.shape == (2, 16, 2048)
    assert s1_tokens.shape == (2, 16, 2048)

def test_satquery_vqa_model_postprocessing_bboxes():
    vqa = SatQueryVQA(mock_mode=True)
    raw_text = "The built-up area is located at [100, 200, 400, 500]."
    clean_ans, evidence = vqa.postprocess_answer(raw_text, task="referring_lulc_detection")

    assert "bounding_boxes" in evidence
    assert len(evidence["bounding_boxes"]) == 1
    # Normalized [0, 1]
    assert evidence["bounding_boxes"][0] == [0.1, 0.2, 0.4, 0.5]
