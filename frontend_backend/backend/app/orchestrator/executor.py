"""
Agent Task Executor for the SatQuery Central Orchestrator.

Executes planned agents according to their dependency order, handles data passing
between interdependent stages, and provides resilient error isolation.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple

from .schemas import (
    AgentType,
    AgentStatus,
    StandardizedAgentOutput,
    OrchestrationPlan,
)
from .registry import AGENTS, call_vqa_agent, call_grounding_agent, call_change_agent, call_optical_sar_agent, call_area_agent, call_rag_agent
from .trace import TraceManager

logger = logging.getLogger(__name__)


class AgentExecutor:
    """Orchestrates the dependency-ordered execution of selected agents."""

    @staticmethod
    def execute_plan(
        plan: OrchestrationPlan,
        query: str,
        images: List[Any],
        timestamps: Optional[List[str]] = None,
        box_threshold: float = 0.20,
        force_satellite_mode: bool = True,
        trace_manager: Optional[TraceManager] = None,
    ) -> List[StandardizedAgentOutput]:
        """
        Executes agents in batches as specified by the plan's execution_order.
        """
        results: List[StandardizedAgentOutput] = []
        context_data: Dict[str, Any] = {}

        # Resolve primary image and secondary image if available
        primary_image = images[0] if images and len(images) > 0 else None
        secondary_image = images[1] if images and len(images) > 1 else None

        # Resolve timestamps tuple
        ts_tuple: Optional[Tuple[str, str]] = None
        if timestamps and len(timestamps) >= 2:
            ts_tuple = (timestamps[0], timestamps[1])

        for batch_idx, batch in enumerate(plan.execution_order):
            batch_names = [a.value for a in batch]
            logger.info(f"[Orchestrator Executor] Running execution batch {batch_idx + 1}: {batch_names}")

            for agent_type in batch:
                step_start = time.time()
                agent_info = AGENTS.get(agent_type)
                agent_name = agent_info["metadata"].name if agent_info else agent_type.value

                if trace_manager:
                    trace_manager.add_step(
                        name=f"Execute {agent_name}",
                        description=f"Running {agent_name} pipeline for intent '{plan.intent}'",
                        status="running"
                    )

                out: StandardizedAgentOutput

                try:
                    # ── 1. VQA Agent ──
                    if agent_type == AgentType.VQA:
                        out = call_vqa_agent(
                            image=primary_image,
                            question=query,
                            sensor="Sentinel-2"
                        )

                    # ── 2. Object Grounding Agent ──
                    # ── 2. Object Grounding Agent ──
                    elif agent_type == AgentType.GROUNDING:
                        # Extract target label from query if possible (e.g. 'buildings', 'roads')
                        grounding_query = query
                        q_lower = query.lower()
                        if "second" in q_lower or "2nd" in q_lower or "after" in q_lower or "t2" in q_lower:
                            target_img = secondary_image if secondary_image is not None else primary_image
                        elif "first" in q_lower or "1st" in q_lower or "before" in q_lower or "t1" in q_lower:
                            target_img = primary_image if primary_image is not None else secondary_image
                        elif AgentType.CHANGE_DETECTION in plan.selected_agents and secondary_image is not None:
                            target_img = secondary_image
                        else:
                            target_img = primary_image if primary_image is not None else secondary_image

                        out = call_grounding_agent(
                            image=target_img,
                            query=grounding_query,
                            box_threshold=box_threshold
                        )
                        context_data["grounding_count"] = out.measurements.get("detected_count", 0)

                    # ── 3. Change Detection Agent ──
                    elif agent_type == AgentType.CHANGE_DETECTION:
                        out = call_change_agent(
                            image_t1=primary_image,
                            image_t2=secondary_image,
                            question=query,
                            timestamps=ts_tuple
                        )
                        context_data["change_regions"] = out.change_regions

                    # ── 4. Optical-SAR Multimodal Agent ──
                    elif agent_type == AgentType.OPTICAL_SAR:
                        out = call_optical_sar_agent(
                            optical_image=primary_image,
                            sar_image=secondary_image,
                            question=query
                        )

                    # ── 5. Area Management Agent ──
                    elif agent_type == AgentType.AREA_MANAGEMENT:
                        # Smart target image selection based on user query cues (e.g. 2nd image vs 1st image)
                        q_lower = query.lower()
                        if "second" in q_lower or "2nd" in q_lower or "after" in q_lower or "t2" in q_lower or "later" in q_lower:
                            target_img = secondary_image if secondary_image is not None else primary_image
                        elif "first" in q_lower or "1st" in q_lower or "before" in q_lower or "t1" in q_lower or "initial" in q_lower:
                            target_img = primary_image if primary_image is not None else secondary_image
                        elif AgentType.CHANGE_DETECTION in plan.selected_agents and secondary_image is not None:
                            target_img = secondary_image
                        else:
                            target_img = primary_image if primary_image is not None else secondary_image

                        out = call_area_agent(
                            image=target_img,
                            force_satellite_mode=force_satellite_mode
                        )

                    # ── 6. RAG Domain Knowledge Agent ──
                    elif agent_type == AgentType.RAG:
                        out = call_rag_agent(query=query)

                    else:
                        out = StandardizedAgentOutput(
                            agent=agent_type,
                            agent_name=agent_name,
                            status=AgentStatus.SKIPPED,
                            error=f"Unrecognized agent type: {agent_type}"
                        )

                except Exception as e:
                    logger.error(f"[Orchestrator Executor] Error running {agent_name}: {e}", exc_info=True)
                    out = StandardizedAgentOutput(
                        agent=agent_type,
                        agent_name=agent_name,
                        status=AgentStatus.FAILED,
                        error=str(e),
                        execution_time_seconds=time.time() - step_start
                    )

                step_duration = time.time() - step_start
                out.execution_time_seconds = step_duration

                if trace_manager:
                    status_str = "completed" if out.status == AgentStatus.SUCCESS else "failed"
                    trace_manager.add_step(
                        name=f"Completed {agent_name}",
                        description=f"{agent_name} finished in {step_duration:.2f}s (Status: {out.status.value})",
                        status=status_str,
                        duration_seconds=step_duration,
                        details={"confidence": out.confidence, "error": out.error}
                    )
                    if out.error:
                        trace_manager.record_error(f"{agent_name}: {out.error}")

                results.append(out)

        return results
