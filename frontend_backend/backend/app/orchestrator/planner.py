"""
Task Planner and Query Understanding for the SatQuery Central Orchestrator.

Analyzes the user's natural-language query to determine:
1. User intent
2. Required task(s) and selected agent(s)
3. Input validation requirements (single scene, temporal pair, optical+SAR)
4. Ambiguity / clarification needs
5. Dependency-aware execution order (sequential vs parallel batches)
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from .schemas import AgentType, OrchestrationPlan
from .prompts import CLARIFICATION_AMBIGUOUS_QUERY


# Keywords and patterns for intent classification
AMBIGUOUS_QUERIES = {
    "analyze this",
    "analyze this image",
    "analyze image",
    "analyze",
    "tell me about this",
    "check this",
    "run analysis",
    "inspect this",
    "what do you see",
}

RAG_KEYWORDS = [
    r"\bwhat is (sar|sentinel|ndvi|gsd|c-band|polaris|radar|cartosat|modis|landsat|lidar)\b",
    r"\bwhy is sar useful\b",
    r"\bexplain the difference\b",
    r"\bexplain what sar is\b",
    r"\bwhat does sar mean\b",
    r"\bwhat is risat\b",
    r"\bwhat is isro\b",
    r"\bdefinition of\b",
]

SAR_MULTIMODAL_KEYWORDS = [
    r"\boptical\s+(and|\+)\s+sar\b",
    r"\bsar\s+show\s+that\s+optical\s+does\s+not\b",
    r"\boptical\s+does\s+not\b",
    r"\bradar\s+vs\s+optical\b",
    r"\bbackscatter\b",
    r"\bmicrowave\s+backscatter\b",
    r"\bflood\s+under\s+clouds\b",
    r"\bpenetrate\s+clouds\b",
]

TEMPORAL_CHANGE_KEYWORDS = [
    r"\bbetween\s+\d{4}\s+and\s+\d{4}\b",
    r"\bwhat\s+changed\b",
    r"\bhas\s+this\s+area\s+(expanded|grown|changed)\b",
    r"\bchanged\s+regions\b",
    r"\bnew\s+buildings\b",
    r"\bnew\s+structures\b",
    r"\burban\s+expansion\b",
    r"\bover\s+time\b",
    r"\badded\s+between\b",
    r"\bdifference\s+between\s+\d{4}\b",
]

GROUNDING_KEYWORDS = [
    r"\bfind\s+(all\s+)?(buildings|runways|roads|structures|vehicles|ships|airplanes|tanks|bridges|houses)\b",
    r"\blocate\s+(the\s+|all\s+)?(runways|buildings|roads|bridges|structures)\b",
    r"\bshow\s+(all\s+)?(roads|buildings|runways|structures)\b",
    r"\bhow\s+many\s+(buildings|structures|roads|runways|vehicles|houses)\s+(are\s+there|were|visible|detected)\b",
    r"\bcount\s+(the\s+|all\s+)?(buildings|structures|vehicles|roads)\b",
    r"\bdetect\s+(all\s+)?(buildings|structures|roads|runways)\b",
    r"\bbounding\s+boxes\b",
]

AREA_KEYWORDS = [
    r"\bpercentage\s+of\s+(the\s+area|this\s+area|land|water|vegetation|urban|forest)\b",
    r"\bhow\s+much\s+area\b",
    r"\bhow\s+much\s+land\b",
    r"\bcalculate\s+.*area\b",
    r"\baffected\s+area\b",
    r"\bchanged\s+area\b",
    r"\bestimate\s+(the\s+)?area\b",
    r"\bcovered\s+by\s+(water|buildings|vegetation|forest|urban)\b",
    r"\barea\s+of\s+(the\s+changed\s+region|water|vegetation|buildings|structures)\b",
    r"\bland[-\s]cover\b",
    r"\bhectares\b",
]


class QueryPlanner:
    """Intelligent planner that converts user queries into multi-agent execution graphs."""

    @staticmethod
    def plan(
        query: str,
        image_count: int = 1,
        has_temporal_metadata: bool = False,
        has_sar_metadata: bool = False,
    ) -> OrchestrationPlan:
        """
        Parses the query and input characteristics to generate an OrchestrationPlan.
        """
        q_clean = query.strip().lower()

        # ── 1. Check for Ambiguous Query ──
        # If the query is an ultra-short generic inquiry ("analyze this")
        normalized_q = re.sub(r"[^\w\s]", "", q_clean).strip()
        if normalized_q in AMBIGUOUS_QUERIES or (
            normalized_q.startswith("analyze") and len(normalized_q.split()) <= 3 and not any(k in normalized_q for k in ["sar", "change", "building", "area", "water", "road", "between"])
        ):
            return OrchestrationPlan(
                intent="Ambiguous / General Analysis Request",
                primary_goal="Provide interactive analysis options",
                is_ambiguous=True,
                clarification_message=CLARIFICATION_AMBIGUOUS_QUERY,
                selected_agents=[],
                execution_order=[],
                selection_reasoning="The query is broad and ambiguous. Asking user for the intended analysis focus.",
            )

        # ── 2. Detect Component Intents ──
        requires_temporal = False
        requires_grounding = False
        requires_change = False
        requires_sar = False
        requires_area = False
        requires_rag = False

        # Temporal change check
        for pattern in TEMPORAL_CHANGE_KEYWORDS:
            if re.search(pattern, q_clean):
                requires_temporal = True
                requires_change = True
                break

        # Grounding check
        for pattern in GROUNDING_KEYWORDS:
            if re.search(pattern, q_clean):
                requires_grounding = True
                break
        if "new buildings" in q_clean or "new structures" in q_clean:
            requires_grounding = True

        # Area check
        for pattern in AREA_KEYWORDS:
            if re.search(pattern, q_clean):
                requires_area = True
                break

        # SAR check
        for pattern in SAR_MULTIMODAL_KEYWORDS:
            if re.search(pattern, q_clean):
                requires_sar = True
                break

        # RAG check
        for pattern in RAG_KEYWORDS:
            if re.search(pattern, q_clean):
                requires_rag = True
                break

        # Additional RAG heuristics (conceptual domain explanations)
        if "explain why" in q_clean or "why is" in q_clean or "what is sar" in q_clean or "tell me about sentinel" in q_clean:
            requires_rag = True

        # Pure RAG check: query is asking conceptual domain knowledge without referring to an uploaded image
        is_pure_concept = any(q_clean.startswith(prefix) for prefix in ["what is ", "what are ", "explain ", "why is ", "difference between "])
        has_image_ref = any(term in q_clean for term in ["this image", "in this", "these images", "uploaded", "here", "scene"])
        if is_pure_concept and not has_image_ref and not (requires_change or requires_grounding or requires_area):
            requires_rag = True
            requires_sar = False

        # ── 3. Combine Intents and Select Agents ──
        selected_agents: List[AgentType] = []
        execution_order: List[List[AgentType]] = []
        reasoning_parts: List[str] = []
        intent = "General Inquiry"

        # Multi-Agent: Change + Grounding + Area
        if requires_change and requires_grounding and requires_area:
            intent = "Temporal Object Change Detection & Area Quantification"
            selected_agents = [AgentType.CHANGE_DETECTION, AgentType.GROUNDING, AgentType.AREA_MANAGEMENT]
            execution_order = [
                [AgentType.CHANGE_DETECTION],
                [AgentType.GROUNDING, AgentType.AREA_MANAGEMENT],
            ]
            reasoning_parts = [
                "Two dates / temporal comparison detected -> Change Detection Agent",
                "Specific object localization requested -> Object Grounding Agent",
                "Area calculation or percentage requested -> Area Management AI",
            ]

        # Multi-Agent: Change + Grounding
        elif requires_change and requires_grounding:
            intent = "Temporal Object Change Detection"
            selected_agents = [AgentType.CHANGE_DETECTION, AgentType.GROUNDING]
            execution_order = [
                [AgentType.CHANGE_DETECTION],
                [AgentType.GROUNDING],
            ]
            reasoning_parts = [
                "Temporal comparison detected -> Change Detection Agent",
                "Target objects (e.g. buildings) specified -> Object Grounding Agent",
            ]

        # Multi-Agent: Change + Area
        elif requires_change and requires_area:
            intent = "Temporal Change & Area Quantification"
            selected_agents = [AgentType.CHANGE_DETECTION, AgentType.AREA_MANAGEMENT]
            execution_order = [
                [AgentType.CHANGE_DETECTION],
                [AgentType.AREA_MANAGEMENT],
            ]
            reasoning_parts = [
                "Change detection requested between dates -> Change Detection Agent",
                "Area quantification requested -> Area Management AI",
            ]

        # Multi-Agent: Optical-SAR + RAG
        elif requires_sar and requires_rag:
            intent = "Optical-SAR Multimodal Analysis & Domain Explanation"
            selected_agents = [AgentType.OPTICAL_SAR, AgentType.RAG]
            execution_order = [
                [AgentType.OPTICAL_SAR, AgentType.RAG],
            ]
            reasoning_parts = [
                "Multimodal Optical and SAR imagery analysis requested -> Optical-SAR Agent",
                "Domain knowledge explanation requested -> RAG Knowledge Agent",
            ]

        # Single Agent: Change Detection
        elif requires_change:
            intent = "Temporal Change Detection"
            selected_agents = [AgentType.CHANGE_DETECTION]
            execution_order = [[AgentType.CHANGE_DETECTION]]
            reasoning_parts = ["Temporal comparison or change inquiry detected -> Change Detection Agent"]

        # Single Agent: Grounding
        elif requires_grounding:
            intent = "Object Grounding & Localization"
            selected_agents = [AgentType.GROUNDING]
            execution_order = [[AgentType.GROUNDING]]
            reasoning_parts = ["Object localization or counting query detected -> Object Grounding Agent"]

        # Single Agent: Area Management
        elif requires_area:
            intent = "Land-Cover Area & Coverage Measurement"
            selected_agents = [AgentType.AREA_MANAGEMENT]
            execution_order = [[AgentType.AREA_MANAGEMENT]]
            reasoning_parts = ["Area measurement or coverage percentage query detected -> Area Management AI"]

        # Single Agent: Optical-SAR
        elif requires_sar:
            intent = "Optical-SAR Multimodal Fusion Analysis"
            selected_agents = [AgentType.OPTICAL_SAR]
            execution_order = [[AgentType.OPTICAL_SAR]]
            reasoning_parts = ["SAR microwave vs optical reflectance inquiry detected -> Optical-SAR Agent"]

        # Single Agent: RAG Domain Knowledge
        elif requires_rag:
            intent = "Remote Sensing Domain Knowledge Retrieval"
            selected_agents = [AgentType.RAG]
            execution_order = [[AgentType.RAG]]
            reasoning_parts = ["Domain concept, sensor definition, or theoretical question -> RAG Knowledge Agent"]

        # Default Single Agent: Visual Question Answering (VQA)
        else:
            intent = "Visual Question Answering"
            selected_agents = [AgentType.VQA]
            execution_order = [[AgentType.VQA]]
            reasoning_parts = ["Natural-language visual reasoning over satellite scene -> VQA Agent"]

        selection_reasoning = "; ".join(reasoning_parts)

        # ── 4. Input Validation Check ──
        missing_inputs = []
        if AgentType.CHANGE_DETECTION in selected_agents and image_count < 2 and not has_temporal_metadata:
            missing_inputs.append("Two temporal satellite scenes from different dates (T1 and T2)")

        return OrchestrationPlan(
            intent=intent,
            primary_goal=f"Execute {', '.join([a.value for a in selected_agents])}",
            requires_temporal=requires_temporal,
            requires_grounding=requires_grounding,
            requires_change=requires_change,
            requires_sar=requires_sar,
            requires_area=requires_area,
            requires_rag=requires_rag,
            is_ambiguous=False,
            selected_agents=selected_agents,
            execution_order=execution_order,
            selection_reasoning=selection_reasoning,
            missing_inputs=missing_inputs,
        )
