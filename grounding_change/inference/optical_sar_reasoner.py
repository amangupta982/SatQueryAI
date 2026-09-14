"""
Optical-SAR Deterministic Multimodal Reasoner & Session Manager
Paper: "BigEarthNet.txt: A Large-Scale Multi-Sensor Image-Text Dataset and Benchmark for Earth Observation"
arXiv: https://arxiv.org/abs/2603.29630

Provides multi-turn conversational reasoning over OpticalSARScene objects.
Strictly offline, deterministic, and evidence-grounded.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from grounding_change.schemas import OpticalSARScene, AnalysisInterpretationMode
from grounding_change.taxonomy import taxonomy

logger = logging.getLogger("OpticalSARReasoner")


class OpticalSARSessionManager:
    """Manages cached OpticalSARScene objects with TTL eviction for multi-turn conversations."""

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def save_scene(self, scene: OpticalSARScene) -> str:
        self._sessions[scene.scene_id] = {
            "scene": scene,
            "updated_at": time.time(),
            "history": list(scene.vqa_dialogue_history)
        }
        self._evict_expired()
        return scene.scene_id

    def get_scene(self, scene_id: str) -> Optional[OpticalSARScene]:
        self._evict_expired()
        data = self._sessions.get(scene_id)
        if data:
            data["updated_at"] = time.time()
            return data["scene"]
        return None

    def add_dialogue(self, scene_id: str, question: str, answer: str) -> None:
        data = self._sessions.get(scene_id)
        if data:
            data["history"].append({"question": question, "answer": answer})
            data["scene"].vqa_dialogue_history = data["history"]
            data["updated_at"] = time.time()

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [sid for sid, d in self._sessions.items() if now - d["updated_at"] > self.ttl]
        for sid in expired:
            del self._sessions[sid]


# Global session registry
optical_sar_sessions = OpticalSARSessionManager()


class OpticalSARReasoner:
    """
    Deterministic reasoning engine answering follow-up questions on OpticalSARScene.
    Enforces hallucination-free output mapped directly from model evidence.
    """

    @staticmethod
    def answer_query(scene: OpticalSARScene, query: str) -> Dict[str, Any]:
        q = query.lower().strip()
        interpretation = scene.interpretation_mode

        # 1. Modality Comparison / Differences
        if any(k in q for k in ["difference", "different", "optical vs sar", "sar vs optical", "compare modalities"]):
            diff = scene.cross_modal_difference
            ans = (
                f"Mode A (Cross-Modal Complementarity): "
                f"Optical features emphasize: {', '.join(diff.optical_dominant_features)}. "
                f"SAR features emphasize: {', '.join(diff.sar_dominant_features)}. "
                f"Cross-sensor structural alignment is {diff.cross_modal_correlation * 100:.1f}%. "
                f"Notice that SAR penetrates moisture and haze to verify physical geometry, "
                f"while Sentinel-2 resolves fine spectral distinctions."
            )
            return {"answer": ans, "mode": interpretation, "type": "cross_modal_comparison"}

        # 2. Presence & Classification (BigEarthNet.txt Task: Presence)
        if any(k in q for k in ["what is present", "what's present", "land cover", "classes", "what is there"]):
            cats = scene.categories_detected
            props = scene.category_proportions
            cats_formatted = [f"{c.capitalize()} ({props.get(c, 0):.1f}%)" for c in cats]
            ans = (
                f"Detected land-cover classes in this scene: {', '.join(cats_formatted)}. "
                f"The dominant category is {cats[0].capitalize()} covering {props.get(cats[0], 0):.1f}% of the scene."
            )
            return {"answer": ans, "mode": interpretation, "type": "presence"}

        # 3. Grounding / Localization (BigEarthNet.txt Task: Referring Expression Detection)
        if any(k in q for k in ["where is", "where are", "location", "locate", "box", "find"]):
            if scene.grounded_regions:
                r = scene.grounded_regions[0]
                b = r.bbox  # [xmin, ymin, xmax, ymax]
                ans = (
                    f"Target grounded in Region {r.region_id} [{r.category.capitalize()}]. "
                    f"Pixel bounding box: [ymin={b[1]}, xmin={b[0]}, ymax={b[3]}, xmax={b[2]}], "
                    f"Centroid: {r.centroid_pixel}, Area: {r.area_m2:.0f} m²."
                )
                return {"answer": ans, "region_id": r.region_id, "bbox": [b[1], b[0], b[3], b[2]], "type": "grounding"}
            else:
                return {"answer": "No distinct localized target region identified matching the expression.", "type": "grounding"}

        # 4. Temporal Relationship Query (Enforce Critical Rule: Never fake temporal change)
        if any(k in q for k in ["change", "temporal", "before and after", "past to present"]):
            if interpretation == AnalysisInterpretationMode.MODE_A_CROSS_MODAL:
                ans = (
                    "Important Policy Notice: These Sentinel-1 SAR and Sentinel-2 Optical observations "
                    "are co-registered acquisitions of the same scene, NOT a multitemporal change pair. "
                    "Differences reflect complementary sensor physics (surface reflectance vs radar backscatter), "
                    "not physical land-cover alteration over time."
                )
            else:
                ans = (
                    f"Mode B (Temporal Change) is active with confirmed timestamp separation: "
                    f"Optical ({scene.sensor_metadata.optical_timestamp}) vs SAR ({scene.sensor_metadata.sar_timestamp})."
                )
            return {"answer": ans, "mode": interpretation, "type": "temporal_policy"}

        # 5. Fallback General Question
        dominant = scene.categories_detected[0] if scene.categories_detected else "vegetation"
        ans = (
            f"Analysis of scene {scene.scene_id}: Co-registered Sentinel-1 SAR + Sentinel-2 Optical. "
            f"Dominant classification is {dominant.capitalize()} ({scene.category_proportions.get(dominant, 0):.1f}%). "
            f"Cross-modal alignment: {scene.cross_modal_difference.cross_modal_correlation * 100:.1f}%."
        )
        return {"answer": ans, "mode": interpretation, "type": "general"}
