"""Inference, evidence extraction, and extension adapters for SatQuery-VQA."""
from vqa_captioning.inference.predictor import SatQueryPredictor
from vqa_captioning.inference.evidence_extractor import EvidenceExtractor
from vqa_captioning.inference.adapters import CountEvidenceAdapter, LandCoverEvidenceAdapter, AreaCalculator

__all__ = [
    "SatQueryPredictor",
    "EvidenceExtractor",
    "CountEvidenceAdapter",
    "LandCoverEvidenceAdapter",
    "AreaCalculator",
]
