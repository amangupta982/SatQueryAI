"""
High-level prediction interface for SatQuery-VQA.
Provides `SatQueryPredictor.ask(image, question)` and routes to evidence adapters.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from PIL import Image
import numpy as np

from vqa_captioning.models.satquery_vqa_model import SatQueryVQA
from vqa_captioning.inference.adapters import CountEvidenceAdapter, LandCoverEvidenceAdapter
from vqa_captioning.inference.evidence_extractor import EvidenceExtractor

class SatQueryPredictor:
    """
    Main inference interface for SatQuery-VQA.
    Used by CLI, FastAPI backend, and agent_rag module.
    """

    def __init__(
        self,
        model_name_or_path: str = "Qwen/Qwen2.5-VL-3B-Instruct",
        adapter_path: Optional[str] = None,
        external_detector_fn: Optional[Any] = None,
        **kwargs,
    ):
        self.model = SatQueryVQA(
            model_name_or_path=model_name_or_path,
            adapter_path=adapter_path,
            **kwargs,
        )
        self.count_adapter = CountEvidenceAdapter(external_detector_fn=external_detector_fn)
        self.area_adapter = LandCoverEvidenceAdapter()
        self.evidence_extractor = EvidenceExtractor()

    def ask(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        question: str,
        sensor: str = "Sentinel-2",
        segmentation_mask: Optional[np.ndarray] = None,
        choices: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Public interface: Takes an image and a natural language question.
        Returns:
            {
                "answer": str,
                "confidence": float or None,
                "task": str,
                "evidence": dict,
                "model": "SatQuery-VQA"
            }
        """
        q_clean = question.strip()
        q_low = q_clean.lower()

        # Route counting queries through CountEvidenceAdapter
        if "how many" in q_low or q_low.startswith("count "):
            return self.count_adapter.handle_count_query(
                image_input=image,
                question=q_clean,
                vqa_model_fn=lambda img, q, task: self.model.predict(img, q, task=task, sensor=sensor),
            )

        # Route exact area queries through LandCoverEvidenceAdapter if mask supplied
        if segmentation_mask is not None and any(w in q_low for w in ["percentage", "area", "cover", "fraction"]):
            return self.area_adapter.handle_area_query(
                image_input=image,
                question=q_clean,
                vqa_model_fn=lambda img, q, task: self.model.predict(img, q, task=task, sensor=sensor),
                segmentation_mask=segmentation_mask,
            )

        # General VQA / Grounding / Land Cover query
        res = self.model.predict(
            image=image,
            question=q_clean,
            sensor=sensor,
            choices=choices,
        )

        # Enhance evidence with EvidenceExtractor
        compiled_evidence = self.evidence_extractor.compile_evidence(
            raw_answer=res.get("answer", ""),
            task=res.get("task", ""),
            sensor_metadata=res.get("evidence", {}),
        )
        res["evidence"] = compiled_evidence
        return res
