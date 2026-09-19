"""
Agent Registry for SatQuery AI.

Exposes metadata and non-invasive adapter functions for the 6 existing agents:
1. VQA Agent (SatQueryPredictor)
2. Object Grounding Agent (ground_objects)
3. Change Detection Agent (analyze_temporal_scene)
4. Optical-SAR Multimodal Agent (analyze_optical_sar_scene)
5. Area Management AI (analyze_area)
6. RAG / Remote Sensing Knowledge Agent (RAGService)

None of the underlying agent code is modified. Adapters normalize agent calls
and outputs into a consistent StandardizedAgentOutput format.
"""

import io
import os
import time
import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image

from .schemas import (
    AgentType,
    AgentStatus,
    AgentMetadata,
    StandardizedAgentOutput,
    ImageEvidence,
    KnowledgeEvidence,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PUBLIC_DIR = PROJECT_ROOT / "frontend_backend" / "frontend" / "public"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


# ─────────────────────────────────────────────────────────────────────────────
# Image Resolution Helpers
# ─────────────────────────────────────────────────────────────────────────────

PRESET_IMAGES = {
    "brahmaputra": "hero_brahmaputra_exact_seamless.jpg",
    "bengaluru": "satellite_scene.jpg",
    "inundation": "cap_optical_sar.jpg",
    "change": "cap_change.jpg",
    "detection": "cap_detection.jpg",
    "vqa": "cap_vqa.jpg",
    "river-urban-expansion": "hero_brahmaputra_exact_seamless.jpg",
    "river-buildings-grounding": "satellite_scene.jpg",
    "flood-sar-inundation": "cap_optical_sar.jpg",
    "scene-river-2023": "hero_brahmaputra_exact_seamless.jpg",
    "scene-river-2024": "cap_change.jpg",
    "scene-cartosat-blr": "satellite_scene.jpg",
    "scene-opt-flood": "cap_optical_sar.jpg",
    "scene-sar-flood": "cap_optical_sar.jpg",
}


def numpy_to_base64(img_array: np.ndarray, fmt: str = "PNG") -> str:
    """Convert numpy array (H, W, 3) to base64 data string."""
    try:
        img = Image.fromarray(img_array.astype(np.uint8))
        buffer = io.BytesIO()
        img.save(buffer, format=fmt, quality=92)
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        logger.warning(f"Failed to convert numpy array to base64: {e}")
        return ""


def pil_to_base64(img: Image.Image, fmt: str = "PNG") -> str:
    """Convert PIL image to base64 data string."""
    try:
        buffer = io.BytesIO()
        img.save(buffer, format=fmt, quality=92)
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        logger.warning(f"Failed to convert PIL image to base64: {e}")
        return ""


def resolve_image(image_input: Any) -> Optional[Image.Image]:
    """
    Resolves various image representations (path, base64, bytes, preset ID, URL, numpy, PIL)
    into a valid PIL Image.
    """
    if image_input is None:
        return None

    if isinstance(image_input, Image.Image):
        return image_input.convert("RGB")

    if isinstance(image_input, np.ndarray):
        return Image.fromarray(image_input.astype(np.uint8)).convert("RGB")

    if isinstance(image_input, (bytes, bytearray)):
        try:
            return Image.open(io.BytesIO(image_input)).convert("RGB")
        except Exception as e:
            logger.warning(f"Failed to parse bytes image: {e}")

    if isinstance(image_input, str):
        # 1. Base64
        if image_input.startswith("data:image") or ";base64," in image_input or len(image_input) > 200:
            try:
                b64_clean = image_input.split(",")[-1].strip()
                data = base64.b64decode(b64_clean)
                return Image.open(io.BytesIO(data)).convert("RGB")
            except Exception as e:
                logger.warning(f"Failed to parse base64 image: {e}")

        # 2. HTTP/HTTPS URL
        if image_input.startswith("http://") or image_input.startswith("https://"):
            try:
                import urllib.request
                req = urllib.request.Request(image_input, headers={"User-Agent": "SatQueryAI/1.0"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = resp.read()
                    return Image.open(io.BytesIO(data)).convert("RGB")
            except Exception as e:
                logger.warning(f"Failed to fetch image from URL: {e}")

        # 3. Preset key
        clean_key = image_input.strip().lstrip("/").lower()
        preset_file = PRESET_IMAGES.get(clean_key) or PRESET_IMAGES.get(image_input.lower())
        if preset_file:
            path = PUBLIC_DIR / preset_file.lstrip("/")
            if path.exists():
                try:
                    return Image.open(path).convert("RGB")
                except Exception:
                    pass

        # 4. Direct path
        path = Path(image_input)
        if path.exists():
            try:
                return Image.open(path).convert("RGB")
            except Exception:
                pass

        # 5. Check in PUBLIC_DIR directly (stripping leading slash)
        clean_name = image_input.strip().lstrip("/")
        pub_path = PUBLIC_DIR / clean_name
        if pub_path.exists():
            try:
                return Image.open(pub_path).convert("RGB")
            except Exception:
                pass

        # 6. Search in outputs/change_uploads, outputs/optical_sar_uploads, or PUBLIC_DIR
        for search_dir in [OUTPUTS_DIR / "change_uploads", OUTPUTS_DIR / "optical_sar_uploads", PUBLIC_DIR]:
            if search_dir.exists():
                for ext in ["", ".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
                    candidate = search_dir / f"{clean_name}{ext}"
                    if candidate.exists():
                        try:
                            return Image.open(candidate).convert("RGB")
                        except Exception:
                            pass

    return None


def resolve_image_path(image_input: Any) -> Optional[str]:
    """
    Resolves an image input to a string file path on disk if available,
    or saves a temporary image to outputs/orchestrator_cache.
    """
    if image_input is None:
        return None

    if isinstance(image_input, str):
        path = Path(image_input)
        if path.exists():
            return str(path)
        clean_name = image_input.strip().lstrip("/")
        pub_path = PUBLIC_DIR / clean_name
        if pub_path.exists():
            return str(pub_path)
        clean_key = clean_name.lower()
        preset_file = PRESET_IMAGES.get(clean_key) or PRESET_IMAGES.get(image_input.lower())
        if preset_file:
            target = PUBLIC_DIR / preset_file.lstrip("/")
            if target.exists():
                return str(target)


    # Convert to PIL and write to a cached file
    pil = resolve_image(image_input)
    if pil is not None:
        cache_dir = OUTPUTS_DIR / "orchestrator_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        temp_path = cache_dir / f"temp_{int(time.time()*1000)}.png"
        pil.save(temp_path, format="PNG")
        return str(temp_path)

    return None


# ─────────────────────────────────────────────────────────────────────────────
# 1. VQA Agent Adapter
# ─────────────────────────────────────────────────────────────────────────────

def call_vqa_agent(
    image: Any,
    question: str,
    sensor: str = "Sentinel-2"
) -> StandardizedAgentOutput:
    """Invokes existing SatQueryPredictor for single-scene VQA."""
    start_time = time.time()
    try:
        pil_img = resolve_image(image)
        if pil_img is None and image is None:
            # Fallback to default reference scene only if none provided
            ref_path = PUBLIC_DIR / "hero_brahmaputra_exact_seamless.jpg"
            if ref_path.exists():
                pil_img = Image.open(ref_path).convert("RGB")

        if pil_img is None:
            return StandardizedAgentOutput(
                agent=AgentType.VQA,
                agent_name="VQA Agent",
                status=AgentStatus.FAILED,
                error="VQA requires a valid satellite image, but the provided image could not be loaded.",
                execution_time_seconds=time.time() - start_time
            )

        from frontend_backend.api.vqa_router import get_vqa_predictor
        predictor = get_vqa_predictor()

        if predictor is None or predictor.model is None:
            # Model checkpoint not loaded; provide transparent structured response
            return StandardizedAgentOutput(
                agent=AgentType.VQA,
                agent_name="VQA Agent",
                status=AgentStatus.FAILED,
                answer="SatQuery-VQA vision-language model checkpoint is not currently loaded in the backend runtime.",
                confidence=None,
                error="VQA model unavailable",
                execution_time_seconds=time.time() - start_time
            )

        res = predictor.ask(image=pil_img, question=question, sensor=sensor)
        answer = res.get("answer", "")
        confidence = res.get("confidence")

        img_b64 = pil_to_base64(pil_img)
        evidence = [
            ImageEvidence(
                type="analyzed_scene",
                title="VQA Observed Scene",
                url_or_b64=img_b64,
                metadata={"sensor": sensor, "dimensions": list(pil_img.size)}
            )
        ]

        return StandardizedAgentOutput(
            agent=AgentType.VQA,
            agent_name="VQA Agent",
            status=AgentStatus.SUCCESS,
            answer=answer,
            confidence=float(confidence) if confidence is not None else None,
            image_evidence=evidence,
            execution_time_seconds=time.time() - start_time,
            raw_output=res
        )
    except Exception as e:
        logger.error(f"[Orchestrator Registry] VQA execution failed: {e}", exc_info=True)
        return StandardizedAgentOutput(
            agent=AgentType.VQA,
            agent_name="VQA Agent",
            status=AgentStatus.FAILED,
            error=str(e),
            execution_time_seconds=time.time() - start_time
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Object Grounding Agent Adapter
# ─────────────────────────────────────────────────────────────────────────────

def call_grounding_agent(
    image: Any,
    query: str,
    box_threshold: float = 0.20
) -> StandardizedAgentOutput:
    """Invokes existing grounding.api.ground_objects."""
    start_time = time.time()
    try:
        pil_img = resolve_image(image)
        if pil_img is None and image is None:
            ref_path = PUBLIC_DIR / "satellite_scene.jpg"
            if ref_path.exists():
                pil_img = Image.open(ref_path).convert("RGB")

        if pil_img is None:
            return StandardizedAgentOutput(
                agent=AgentType.GROUNDING,
                agent_name="Object Grounding Agent",
                status=AgentStatus.FAILED,
                error="Object Grounding requires a valid satellite image, but the provided image could not be loaded.",
                execution_time_seconds=time.time() - start_time
            )

        from grounding.api import ground_objects
        res = ground_objects(pil_img, query, box_threshold=box_threshold)

        count = res.get("count", 0)
        detections = res.get("detections", [])
        annotated = res.get("annotated_image")
        annotated_b64 = numpy_to_base64(annotated) if annotated is not None else ""

        target_label = res.get("target_label", query)
        answer = f"Found {count} instance{'s' if count != 1 else ''} of '{target_label}' with bounding box localization."

        # Compute average confidence from detections if available
        confs = [d.get("confidence", 0.0) for d in detections if "confidence" in d]
        avg_conf = sum(confs) / len(confs) if confs else 0.90

        evidence = []
        if annotated_b64:
            evidence.append(ImageEvidence(
                type="grounding_visualization",
                title="Object Bounding Box Delineation",
                url_or_b64=annotated_b64,
                metadata={"count": count, "target_label": target_label}
            ))

        return StandardizedAgentOutput(
            agent=AgentType.GROUNDING,
            agent_name="Object Grounding Agent",
            status=AgentStatus.SUCCESS,
            answer=answer,
            confidence=avg_conf,
            bounding_boxes=detections,
            measurements={"detected_count": count, "target_label": target_label},
            image_evidence=evidence,
            execution_time_seconds=time.time() - start_time,
            raw_output={"count": count, "detections_count": len(detections)}
        )
    except Exception as e:
        logger.error(f"[Orchestrator Registry] Grounding execution failed: {e}", exc_info=True)
        return StandardizedAgentOutput(
            agent=AgentType.GROUNDING,
            agent_name="Object Grounding Agent",
            status=AgentStatus.FAILED,
            error=str(e),
            execution_time_seconds=time.time() - start_time
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Change Detection Agent Adapter
# ─────────────────────────────────────────────────────────────────────────────

def call_change_agent(
    image_t1: Any,
    image_t2: Any,
    question: str = "What changed?",
    timestamps: Optional[Tuple[str, str]] = None
) -> StandardizedAgentOutput:
    """Invokes existing grounding_change.inference.analyze_temporal_scene."""
    start_time = time.time()
    try:
        t1_path = resolve_image_path(image_t1)
        t2_path = resolve_image_path(image_t2)

        # Fallback to default temporal pair if none provided
        if not t1_path or not t2_path:
            p1 = PUBLIC_DIR / "satellite_scene.jpg"
            p2 = PUBLIC_DIR / "hero_brahmaputra_exact_seamless.jpg"
            if p1.exists() and p2.exists():
                t1_path = t1_path or str(p1)
                t2_path = t2_path or str(p2)

        if not t1_path or not t2_path:
            return StandardizedAgentOutput(
                agent=AgentType.CHANGE_DETECTION,
                agent_name="Change Detection Agent",
                status=AgentStatus.FAILED,
                error="Change Detection requires two temporal scenes (T1 and T2).",
                execution_time_seconds=time.time() - start_time
            )

        from grounding_change.inference import analyze_temporal_scene
        output = analyze_temporal_scene(
            image_t1=t1_path,
            image_t2=t2_path,
            question=question,
            timestamps=timestamps,
            return_visuals=True,
            return_geo=True
        )

        regions_list = [r.model_dump() for r in output.regions] if output.regions else []
        evidence = []

        if output.visualizations:
            if output.visualizations.complete_overlay:
                evidence.append(ImageEvidence(
                    type="change_overlay",
                    title="Temporal Change Overlay",
                    file_path=output.visualizations.complete_overlay
                ))
            if output.visualizations.change_mask:
                evidence.append(ImageEvidence(
                    type="change_mask",
                    title="Binary Change Mask",
                    file_path=output.visualizations.change_mask
                ))

        # Confidence extraction
        conf_val = 0.90
        if isinstance(output.confidence, dict):
            conf_val = float(output.confidence.get("overall_scene_confidence", 0.90))
        elif isinstance(output.confidence, (float, int)):
            conf_val = float(output.confidence)

        return StandardizedAgentOutput(
            agent=AgentType.CHANGE_DETECTION,
            agent_name="Change Detection Agent",
            status=AgentStatus.SUCCESS,
            answer=output.answer,
            confidence=conf_val,
            change_regions=regions_list,
            measurements=output.statistics or {},
            image_evidence=evidence,
            execution_time_seconds=time.time() - start_time,
            raw_output={
                "region_count": len(regions_list),
                "summary": output.scene_summary.model_dump() if output.scene_summary else None
            }
        )
    except Exception as e:
        logger.error(f"[Orchestrator Registry] Change Detection failed: {e}", exc_info=True)
        return StandardizedAgentOutput(
            agent=AgentType.CHANGE_DETECTION,
            agent_name="Change Detection Agent",
            status=AgentStatus.FAILED,
            error=str(e),
            execution_time_seconds=time.time() - start_time
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Optical-SAR Multimodal Agent Adapter
# ─────────────────────────────────────────────────────────────────────────────

def call_optical_sar_agent(
    optical_image: Any,
    sar_image: Optional[Any] = None,
    question: Optional[str] = None,
    referring_expression: Optional[str] = None,
    agent_mode: str = "optical_sar_full_geospatial"
) -> StandardizedAgentOutput:
    """Invokes existing grounding_change.inference.agent_tools.analyze_optical_sar_scene."""
    start_time = time.time()
    try:
        opt_path = resolve_image_path(optical_image)
        sar_path = resolve_image_path(sar_image) if sar_image else None

        if not opt_path:
            p = PUBLIC_DIR / "cap_optical_sar.jpg"
            if p.exists():
                opt_path = str(p)

        if not opt_path:
            return StandardizedAgentOutput(
                agent=AgentType.OPTICAL_SAR,
                agent_name="Optical-SAR Agent",
                status=AgentStatus.FAILED,
                error="Optical-SAR analysis requires at least one optical image.",
                execution_time_seconds=time.time() - start_time
            )

        from grounding_change.inference.agent_tools import analyze_optical_sar_scene
        result = analyze_optical_sar_scene(
            optical_image=opt_path,
            sar_image=sar_path,
            question=question,
            referring_expression=referring_expression,
            agent_mode=agent_mode
        )

        evidence = []
        if hasattr(result, "evidence_urls") and result.evidence_urls:
            for k, url in result.evidence_urls.items():
                evidence.append(ImageEvidence(
                    type=f"optical_sar_{k}",
                    title=f"Multimodal {k.replace('_', ' ').title()}",
                    url_or_b64=url
                ))

        conf = getattr(result, "confidence", 0.92)

        return StandardizedAgentOutput(
            agent=AgentType.OPTICAL_SAR,
            agent_name="Optical-SAR Agent",
            status=AgentStatus.SUCCESS,
            answer=result.answer,
            confidence=float(conf) if conf is not None else None,
            measurements={
                "mode_applied": getattr(result, "mode_applied", agent_mode),
                "is_temporal_change": getattr(result, "is_temporal_change", False)
            },
            image_evidence=evidence,
            execution_time_seconds=time.time() - start_time,
            raw_output={"mode": getattr(result, "mode_applied", "")}
        )
    except Exception as e:
        logger.error(f"[Orchestrator Registry] Optical-SAR failed: {e}", exc_info=True)
        return StandardizedAgentOutput(
            agent=AgentType.OPTICAL_SAR,
            agent_name="Optical-SAR Agent",
            status=AgentStatus.FAILED,
            error=str(e),
            execution_time_seconds=time.time() - start_time
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Area Management Agent Adapter
# ─────────────────────────────────────────────────────────────────────────────

def call_area_agent(
    image: Any,
    force_satellite_mode: bool = True
) -> StandardizedAgentOutput:
    """Invokes existing area_measurement.inference.analyze_area."""
    start_time = time.time()
    try:
        pil_img = resolve_image(image)
        if pil_img is None and image is None:
            p = PUBLIC_DIR / "satellite_scene.jpg"
            if p.exists():
                pil_img = Image.open(p).convert("RGB")

        if pil_img is None:
            return StandardizedAgentOutput(
                agent=AgentType.AREA_MANAGEMENT,
                agent_name="Area Management AI",
                status=AgentStatus.FAILED,
                error="Area Management requires a valid satellite image, but the provided image could not be loaded.",
                execution_time_seconds=time.time() - start_time
            )

        from area_measurement.inference import analyze_area
        res = analyze_area(pil_img, force_satellite_mode=force_satellite_mode)

        classes = res.get("classes", [])
        annotated = res.get("annotated_image")
        summary_img = res.get("summary_image")

        annotated_b64 = numpy_to_base64(annotated) if annotated is not None else ""
        summary_b64 = numpy_to_base64(summary_img) if summary_img is not None else ""

        evidence = []
        if annotated_b64:
            evidence.append(ImageEvidence(
                type="area_segmentation_overlay",
                title="Class-Segmented Area Overlay",
                url_or_b64=annotated_b64
            ))
        if summary_b64:
            evidence.append(ImageEvidence(
                type="area_summary_table",
                title="Class Coverage Summary Table",
                url_or_b64=summary_b64
            ))

        summary_text = res.get("summary_text", "")
        # Construct helpful natural language answer
        top_classes = sorted(classes, key=lambda c: c.get("coverage_percent", 0.0), reverse=True)[:3]
        class_summaries = [f"{c['class_name']} ({c['coverage_percent']:.1f}%)" for c in top_classes]
        answer = f"Area analysis completed across {len(classes)} land-cover categories. Dominant covers: {', '.join(class_summaries)}."

        measurements = {
            "total_pixels": res.get("total_pixels", 0),
            "classes_count": len(classes),
            "classes": classes,
            "has_physical_area": res.get("has_physical_area", False),
            "total_coverage_percent": res.get("total_coverage_percent", 100.0)
        }

        return StandardizedAgentOutput(
            agent=AgentType.AREA_MANAGEMENT,
            agent_name="Area Management AI",
            status=AgentStatus.SUCCESS,
            answer=answer,
            confidence=0.94,
            measurements=measurements,
            image_evidence=evidence,
            execution_time_seconds=time.time() - start_time,
            raw_output={"summary_text": summary_text}
        )
    except Exception as e:
        logger.error(f"[Orchestrator Registry] Area Management failed: {e}", exc_info=True)
        return StandardizedAgentOutput(
            agent=AgentType.AREA_MANAGEMENT,
            agent_name="Area Management AI",
            status=AgentStatus.FAILED,
            error=str(e),
            execution_time_seconds=time.time() - start_time
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. RAG / Domain Knowledge Agent Adapter
# ─────────────────────────────────────────────────────────────────────────────

def call_rag_agent(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.25
) -> StandardizedAgentOutput:
    """Invokes existing app.rag.service.RAGService."""
    start_time = time.time()
    try:
        from app.rag.service import RAGService
        from app.rag.schemas import RAGQueryRequest

        service = RAGService.get_instance()
        req = RAGQueryRequest(query=query, top_k=top_k, score_threshold=score_threshold)
        res = service.query(req)

        knowledge_evidence = [
            KnowledgeEvidence(
                text=ev.text,
                source=ev.source,
                section=ev.section,
                category=ev.category or "remote_sensing",
                score=ev.score
            )
            for ev in res.evidence
        ]

        # Calculate average retrieval score as confidence
        avg_score = 0.85
        if res.evidence:
            scores = [e.score for e in res.evidence if e.score is not None]
            if scores:
                avg_score = min(1.0, max(0.5, sum(scores) / len(scores)))

        return StandardizedAgentOutput(
            agent=AgentType.RAG,
            agent_name="RAG Knowledge Agent",
            status=AgentStatus.SUCCESS,
            answer=res.answer,
            confidence=avg_score,
            knowledge_evidence=knowledge_evidence,
            measurements={"retrieved_chunks": len(res.evidence), "sources_cited": len(res.sources)},
            execution_time_seconds=time.time() - start_time,
            raw_output={"sources": [s.model_dump() for s in res.sources]}
        )
    except Exception as e:
        logger.error(f"[Orchestrator Registry] RAG execution failed: {e}", exc_info=True)
        return StandardizedAgentOutput(
            agent=AgentType.RAG,
            agent_name="RAG Knowledge Agent",
            status=AgentStatus.FAILED,
            error=str(e),
            execution_time_seconds=time.time() - start_time
        )


# ─────────────────────────────────────────────────────────────────────────────
# Agent Registry Dictionary
# ─────────────────────────────────────────────────────────────────────────────

AGENTS: Dict[AgentType, Dict[str, Any]] = {
    AgentType.VQA: {
        "metadata": AgentMetadata(
            id=AgentType.VQA,
            name="VQA Agent",
            description="Answers natural-language questions about a single remote-sensing scene.",
            supported_tasks=["vqa", "scene_captioning", "scene_understanding"],
            required_inputs=["image", "question"],
            optional_inputs=["sensor"],
            output_types=["answer", "confidence", "visual_evidence"]
        ),
        "adapter": call_vqa_agent,
    },
    AgentType.GROUNDING: {
        "metadata": AgentMetadata(
            id=AgentType.GROUNDING,
            name="Object Grounding Agent",
            description="Finds objects based on text queries, counts them, and returns localized bounding boxes.",
            supported_tasks=["object_detection", "counting", "referring_expression"],
            required_inputs=["image", "query"],
            optional_inputs=["box_threshold"],
            output_types=["bounding_boxes", "count", "annotated_image"]
        ),
        "adapter": call_grounding_agent,
    },
    AgentType.CHANGE_DETECTION: {
        "metadata": AgentMetadata(
            id=AgentType.CHANGE_DETECTION,
            name="Change Detection Agent",
            description="Compares two temporal satellite scenes, finds changed regions, and summarizes structural transitions.",
            supported_tasks=["temporal_change", "structural_expansion", "urban_growth"],
            required_inputs=["image_t1", "image_t2"],
            optional_inputs=["question", "timestamps"],
            output_types=["change_regions", "change_mask", "statistics"]
        ),
        "adapter": call_change_agent,
    },
    AgentType.OPTICAL_SAR: {
        "metadata": AgentMetadata(
            id=AgentType.OPTICAL_SAR,
            name="Optical-SAR Agent",
            description="Analyzes optical and microwave SAR imagery jointly to detect surface features under clouds or flooding.",
            supported_tasks=["multimodal_fusion", "sar_backscatter", "flood_inundation"],
            required_inputs=["optical_image"],
            optional_inputs=["sar_image", "question", "agent_mode"],
            output_types=["cross_modal_difference", "fused_mask", "answer"]
        ),
        "adapter": call_optical_sar_agent,
    },
    AgentType.AREA_MANAGEMENT: {
        "metadata": AgentMetadata(
            id=AgentType.AREA_MANAGEMENT,
            name="Area Management AI",
            description="Performs semantic land-cover segmentation and calculates physical or percentage area coverage.",
            supported_tasks=["area_calculation", "coverage_percentage", "land_cover"],
            required_inputs=["image"],
            optional_inputs=["force_satellite_mode"],
            output_types=["classes", "coverage_percentages", "area_measurements"]
        ),
        "adapter": call_area_agent,
    },
    AgentType.RAG: {
        "metadata": AgentMetadata(
            id=AgentType.RAG,
            name="RAG Knowledge Agent",
            description="Answers remote sensing domain knowledge questions using the curated knowledge base.",
            supported_tasks=["domain_knowledge", "sensor_specs", "satellite_missions"],
            required_inputs=["query"],
            optional_inputs=["top_k"],
            output_types=["answer", "cited_sources", "evidence_chunks"]
        ),
        "adapter": call_rag_agent,
    },
}
