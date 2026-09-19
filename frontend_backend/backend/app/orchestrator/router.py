"""
FastAPI Router for the SatQuery Central Orchestrator.

Endpoints:
  POST /api/orchestrator/query  — Primary natural-language multimodal query endpoint
  POST /api/query               — Alias endpoint for standard API calls
  GET  /api/orchestrator/agents — List all registered agents and capabilities
  GET  /api/orchestrator/health — Health check for the orchestration layer
"""

import time
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import BaseModel

from .schemas import (
    OrchestratorQueryRequest,
    OrchestratorQueryResponse,
    AgentType,
)
from .registry import AGENTS
from .planner import QueryPlanner
from .executor import AgentExecutor
from .aggregator import ResultAggregator
from .trace import TraceManager
from .prompts import CLARIFICATION_AMBIGUOUS_QUERY, MISSING_TEMPORAL_IMAGES_MESSAGE, MISSING_IMAGE_MESSAGE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestrator", tags=["SatQuery Orchestrator"])
alias_router = APIRouter(prefix="/api", tags=["SatQuery Orchestrator"])


def _run_orchestration(
    query: str,
    images: List[Any],
    image_ids: Optional[List[str]] = None,
    timestamps: Optional[List[str]] = None,
    modality: Optional[str] = None,
    box_threshold: float = 0.20,
    force_satellite_mode: bool = True,
) -> OrchestratorQueryResponse:
    """Core orchestration pipeline execution."""
    start_time = time.time()
    trace = TraceManager(query=query)

    # 1. Step: Query Understanding & Task Planning
    t0 = time.time()
    has_temporal = timestamps is not None and len(timestamps) >= 2
    has_sar = (modality or "").lower() == "sar"

    # Multi-scene preset expansion mapping
    PRESET_EXPANSIONS = {
        "river-urban-expansion": ["scene-river-2023", "scene-river-2024"],
        "flood-sar-inundation": ["scene-opt-flood", "scene-sar-flood"],
        "river-buildings-grounding": ["scene-cartosat-blr"],
    }

    # Prioritize real image payloads (base64/bytes/objects) if provided,
    # otherwise fall back to image IDs/preset keys (with expansion for multi-scene presets)
    if images and len(images) > 0:
        all_images = list(images)
    elif image_ids and len(image_ids) > 0:
        expanded_ids = []
        for i_id in image_ids:
            clean_id = str(i_id).strip().lower()
            if clean_id in PRESET_EXPANSIONS:
                expanded_ids.extend(PRESET_EXPANSIONS[clean_id])
                if clean_id == "river-urban-expansion":
                    has_temporal = True
                elif clean_id == "flood-sar-inundation":
                    has_sar = True
            else:
                expanded_ids.append(i_id)
        all_images = expanded_ids
    else:
        all_images = []


    plan = QueryPlanner.plan(
        query=query,
        image_count=len(all_images),
        has_temporal_metadata=has_temporal,
        has_sar_metadata=has_sar,
    )
    planning_duration = time.time() - t0

    trace.set_plan(
        intent=plan.intent,
        selected_agents=plan.selected_agents,
        selection_reasoning=plan.selection_reasoning,
        execution_order=plan.execution_order,
    )
    trace.add_step(
        name="Query Understanding & Intent Parsing",
        description=f"Identified intent: '{plan.intent}'. Selected {len(plan.selected_agents)} agent(s).",
        status="completed",
        duration_seconds=planning_duration,
        details={"reasoning": plan.selection_reasoning}
    )

    # 2. Check for Ambiguity
    if plan.is_ambiguous:
        trace.add_step(
            name="Ambiguity Detection",
            description="Query is ambiguous; returned structured clarification options.",
            status="completed",
            duration_seconds=0.01,
        )
        return OrchestratorQueryResponse(
            success=True,
            query=query,
            intent=plan.intent,
            agents_used=[],
            answer=plan.clarification_message or CLARIFICATION_AMBIGUOUS_QUERY,
            confidence=None,
            confidence_display="Clarification",
            requires_clarification=True,
            clarification_options=[
                "Visual Question Answering (describe/answer scene)",
                "Object Grounding (find & count buildings/infrastructure)",
                "Change Detection (compare two dates)",
                "Optical-SAR (joint multimodal analysis)",
                "Area Management (calculate coverage & hectares)",
                "Domain Knowledge (definitions & sensor theory)",
            ],
            trace=trace.finalize(),
        )

    # 3. Check for Missing Inputs
    if plan.missing_inputs:
        trace.add_step(
            name="Input Validation",
            description=f"Missing required inputs: {', '.join(plan.missing_inputs)}",
            status="warning",
            duration_seconds=0.01,
        )
        msg = f"The requested analysis requires: {', '.join(plan.missing_inputs)}. Please upload or select the appropriate imagery."
        return OrchestratorQueryResponse(
            success=True,
            query=query,
            intent=plan.intent,
            agents_used=[a.value for a in plan.selected_agents],
            answer=msg,
            confidence=None,
            confidence_display="Awaiting Input",
            requires_clarification=True,
            trace=trace.finalize(),
        )

    # 4. Step: Dependency-Aware Agent Execution
    agent_outputs = AgentExecutor.execute_plan(
        plan=plan,
        query=query,
        images=all_images,
        timestamps=timestamps,
        box_threshold=box_threshold,
        force_satellite_mode=force_satellite_mode,
        trace_manager=trace,
    )

    # 5. Step: Result Aggregation & Grounded Answer Synthesis
    t_agg = time.time()
    aggregated = ResultAggregator.aggregate(
        query=query,
        plan=plan,
        agent_outputs=agent_outputs
    )
    agg_duration = time.time() - t_agg

    trace.add_step(
        name="Result Aggregation & Grounded Answer Generation",
        description="Synthesized grounded final response and partitioned evidence.",
        status="completed",
        duration_seconds=agg_duration,
        details={"confidence": aggregated.get("confidence_display")}
    )

    final_trace = trace.finalize()

    return OrchestratorQueryResponse(
        success=True,
        query=query,
        intent=aggregated["intent"],
        agents_used=aggregated["agents_used"],
        answer=aggregated["answer"],
        confidence=aggregated.get("confidence"),
        confidence_display=aggregated.get("confidence_display", "N/A"),
        image_evidence=aggregated["image_evidence"],
        knowledge_evidence=aggregated["knowledge_evidence"],
        measurements=aggregated["measurements"],
        bounding_boxes=aggregated["bounding_boxes"],
        trace=final_trace,
        structured_for_ui=aggregated.get("structured_for_ui"),
        change_data=aggregated.get("change_data"),
    )


# ── JSON Endpoint ──
@router.post("/query", response_model=OrchestratorQueryResponse)
@alias_router.post("/query", response_model=OrchestratorQueryResponse)
async def query_orchestrator(request: OrchestratorQueryRequest):
    """
    Central natural-language query endpoint for SatQuery AI.
    Automatically routes user queries to the appropriate agent(s).
    """
    images = []
    if request.image_b64s:
        images.extend(request.image_b64s)

    return _run_orchestration(
        query=request.query,
        images=images,
        image_ids=request.image_ids,
        timestamps=request.timestamps,
        modality=request.modality,
        box_threshold=request.box_threshold or 0.20,
        force_satellite_mode=request.force_satellite_mode if request.force_satellite_mode is not None else True,
    )


# ── Multipart Form Endpoint (Direct File Upload Support) ──
@router.post("/query-upload", response_model=OrchestratorQueryResponse)
async def query_orchestrator_multipart(
    query: str = Form(..., description="User natural language question"),
    image1: Optional[UploadFile] = File(None, description="Primary satellite scene or T1"),
    image2: Optional[UploadFile] = File(None, description="Secondary scene or T2 / SAR pass"),
    image_ids: Optional[str] = Form(None, description="Comma-separated image IDs or preset names"),
    timestamps: Optional[str] = Form(None, description="Comma-separated timestamps e.g. '2022,2026'"),
    modality: Optional[str] = Form(None, description="Sensor modality hint"),
):
    """
    Multipart upload version of the orchestrator query endpoint.
    Accepts uploaded files directly from HTML/React file inputs.
    """
    loaded_images = []
    if image1 is not None:
        b1 = await image1.read()
        loaded_images.append(b1)
    if image2 is not None:
        b2 = await image2.read()
        loaded_images.append(b2)

    parsed_ids = [s.strip() for s in image_ids.split(",") if s.strip()] if image_ids else None
    parsed_timestamps = [s.strip() for s in timestamps.split(",") if s.strip()] if timestamps else None

    return _run_orchestration(
        query=query,
        images=loaded_images,
        image_ids=parsed_ids,
        timestamps=parsed_timestamps,
        modality=modality,
    )


# ── Registered Agents Metadata Endpoint ──
@router.get("/agents")
def list_registered_agents():
    """Returns metadata and capabilities for all 6 registered agents."""
    return {
        "count": len(AGENTS),
        "agents": [
            {
                "id": a["metadata"].id.value,
                "name": a["metadata"].name,
                "description": a["metadata"].description,
                "supported_tasks": a["metadata"].supported_tasks,
                "required_inputs": a["metadata"].required_inputs,
                "output_types": a["metadata"].output_types,
            }
            for a in AGENTS.values()
        ]
    }


# ── Health Check Endpoint ──
@router.get("/health")
def orchestrator_health():
    """Health check for the central orchestration layer."""
    return {
        "status": "healthy",
        "orchestrator": "SatQuery AI Central Orchestrator",
        "registered_agents": [a.value for a in AgentType],
        "version": "1.0.0"
    }
