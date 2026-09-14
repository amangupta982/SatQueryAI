"""
Unit and Integration Tests for Optical-SAR Multimodal Agent & BigEarthNet.txt
Verifies dataset isolation, foundation encoders, cross-attention fusion,
Mode A (Cross-Modal) vs Mode B (Temporal), and deterministic reasoning.
"""

import pytest
import numpy as np
import torch
from pathlib import Path

from grounding_change.config import settings
from grounding_change.data.download_bigearthnet_txt import BigEarthNetTxtDownloader
from grounding_change.data.adapters.bigearthnet_txt_adapter import BigEarthNetTxtDataset
from grounding_change.models.prithvi_encoder import PrithviEO2OpticalEncoder
from grounding_change.models.summit_sar_encoder import SummitSAREncoder
from grounding_change.models.optical_sar_fusion import OpticalSARFusionModule
from grounding_change.models.multimodal_intelligence_model import MultimodalIntelligenceModel
from grounding_change.inference.optical_sar_pipeline import OpticalSARInferencePipeline
from grounding_change.inference.optical_sar_reasoner import OpticalSARReasoner
from grounding_change.schemas import AnalysisInterpretationMode, MultimodalAgentMode


class TestBigEarthNetDataset:
    """Tests official BigEarthNet.txt downloader and PyTorch adapter."""

    def test_downloader_and_manifest(self, tmp_path):
        downloader = BigEarthNetTxtDownloader(target_dir=tmp_path)
        res = downloader.run(task="vqa", limit=4)
        assert res["status"] == "success"
        assert Path(res["manifest"]).exists()
        assert Path(res["parquet"]).exists()

    def test_adapter_loading(self):
        dataset = BigEarthNetTxtDataset(split="all")
        assert len(dataset) > 0
        sample = dataset[0]
        assert sample.sample_id.startswith("BEN_")
        assert sample.question is not None
        assert sample.metadata["dataset"] == "BigEarthNet.txt"

        mm_sample = dataset.get_multimodal_sample(0)
        assert mm_sample.optical_image.shape[0] == 6  # 6 multispectral bands
        assert mm_sample.sar_image.shape[0] == 2      # VV, VH dual-polarization


class TestFoundationEncoders:
    """Tests Prithvi-EO-2.0 and SUMMIT foundation encoders."""

    def test_prithvi_optical_encoder(self):
        encoder = PrithviEO2OpticalEncoder(in_channels=6, feature_dim=256, img_size=224, depth=2)
        encoder.eval()
        x = torch.randn(1, 6, 224, 224)
        out = encoder(x)
        assert "p2" in out
        assert out["p2"].shape == (1, 256, 56, 56)
        assert out["global_feature"].shape == (1, 1024)

    def test_summit_sar_encoder(self):
        encoder = SummitSAREncoder(in_channels=2, feature_dim=256, img_size=224, depth=2)
        encoder.eval()
        x = torch.randn(1, 2, 224, 224)
        out = encoder(x)
        assert "p2" in out
        assert out["p2"].shape == (1, 256, 56, 56)
        assert out["global_feature"].shape == (1, 768)

    def test_cross_modal_fusion(self):
        fusion = OpticalSARFusionModule(feature_dim=256, num_heads=4)
        fusion.eval()

        opt_feats = {
            "p2": torch.randn(1, 256, 28, 28),
            "p3": torch.randn(1, 256, 14, 14),
            "p4": torch.randn(1, 256, 7, 7),
            "p5": torch.randn(1, 256, 4, 4),
            "global_feature": torch.randn(1, 1024)
        }
        sar_feats = {
            "p2": torch.randn(1, 256, 28, 28),
            "p3": torch.randn(1, 256, 14, 14),
            "p4": torch.randn(1, 256, 7, 7),
            "p5": torch.randn(1, 256, 4, 4),
            "global_feature": torch.randn(1, 768)
        }

        fused = fusion(opt_feats, sar_feats)
        assert "F_fused" in fused
        assert "cross_modal_diff_map" in fused
        assert fused["F_fused"]["p2"].shape == (1, 256, 28, 28)
        assert fused["cross_modal_diff_map"].shape == (1, 1, 28, 28)


class TestOpticalSARPipelineAndModes:
    """Tests Mode A vs Mode B interpretation and reasoning."""

    @pytest.fixture
    def pipeline(self):
        return OpticalSARInferencePipeline(device="cpu")

    def test_mode_a_cross_modal_default(self, pipeline):
        # Same scene without explicit differing dates
        opt = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        sar = np.random.randint(0, 255, (224, 224), dtype=np.uint8)

        output = pipeline.analyze(
            optical_input=opt,
            sar_input=sar,
            question="What land cover classes are present?",
            agent_mode=MultimodalAgentMode.MODE_3_OPTICAL_SAR
        )

        assert output.mode_applied == AnalysisInterpretationMode.MODE_A_CROSS_MODAL
        assert output.is_temporal_change is False
        assert "optical_image" in output.evidence_urls
        assert "sar_image" in output.evidence_urls
        assert "cross_modal_diff" in output.evidence_urls

    def test_mode_b_temporal_change_gated(self, pipeline):
        # Explicitly differing timestamps activates Mode B
        opt = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        sar = np.random.randint(0, 255, (224, 224), dtype=np.uint8)

        output = pipeline.analyze(
            optical_input=opt,
            sar_input=sar,
            question="What changed?",
            optical_timestamp="2018-05-12T10:00:00Z",
            sar_timestamp="2024-05-12T10:00:00Z",
            agent_mode=MultimodalAgentMode.MODE_4_OPTICAL_SAR_TEMPORAL
        )

        assert output.mode_applied == AnalysisInterpretationMode.MODE_B_TEMPORAL_CHANGE
        assert output.is_temporal_change is True

    def test_deterministic_reasoner(self, pipeline):
        opt = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        sar = np.random.randint(0, 255, (224, 224), dtype=np.uint8)

        output = pipeline.analyze(
            optical_input=opt,
            sar_input=sar,
            question="Find water reservoir"
        )

        # 1. Test difference query
        diff_ans = OpticalSARReasoner.answer_query(output.scene, "What is the difference between optical and SAR?")
        assert "Mode A" in diff_ans["answer"]
        assert diff_ans["type"] == "cross_modal_comparison"

        # 2. Test temporal relationship question (policy notice)
        temp_ans = OpticalSARReasoner.answer_query(output.scene, "Tell me what changed from before to after")
        assert "co-registered acquisitions of the same scene, NOT a multitemporal change pair" in temp_ans["answer"]
