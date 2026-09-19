"""
Comprehensive Test Suite for the SatQuery AI Central Orchestration and Routing Layer.

Validates:
1. All 10 User-Specified Routing Scenarios
2. Agent Registry Metadata and Configuration
3. Ambiguity & Clarification Handling
4. Missing Input Pre-check Validation
5. Result Aggregation & Evidence Partitioning (IMAGE_EVIDENCE vs KNOWLEDGE_EVIDENCE)
6. Grounded Confidence Estimation
7. Orchestrator API Endpoints (/api/orchestrator/query, /api/query, /api/orchestrator/agents, /api/orchestrator/health)
8. Regression Checks on Existing Agent Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from frontend_backend.backend.main import app
from frontend_backend.backend.app.orchestrator.schemas import AgentType, StandardizedAgentOutput, ImageEvidence, KnowledgeEvidence
from frontend_backend.backend.app.orchestrator.planner import QueryPlanner
from frontend_backend.backend.app.orchestrator.registry import AGENTS
from frontend_backend.backend.app.orchestrator.aggregator import ResultAggregator


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# =====================================================================
# PART 1: THE 10 SPECIFIED ROUTING SCENARIOS
# =====================================================================

def test_scenario_1_vqa():
    """TEST 1: 'What is in this image?' -> VQA Agent"""
    plan = QueryPlanner.plan("What is in this image?", image_count=1)
    assert not plan.is_ambiguous
    assert plan.selected_agents == [AgentType.VQA]
    assert plan.intent == "Visual Question Answering"


def test_scenario_2_grounding():
    """TEST 2: 'Find all buildings.' -> Grounding Agent"""
    plan = QueryPlanner.plan("Find all buildings.", image_count=1)
    assert not plan.is_ambiguous
    assert plan.selected_agents == [AgentType.GROUNDING]
    assert "Object Grounding" in plan.intent


def test_scenario_3_change_detection():
    """TEST 3: 'What changed between 2022 and 2026?' -> Change Detection Agent"""
    plan = QueryPlanner.plan("What changed between 2022 and 2026?", image_count=2, has_temporal_metadata=True)
    assert not plan.is_ambiguous
    assert plan.selected_agents == [AgentType.CHANGE_DETECTION]
    assert "Temporal Change" in plan.intent


def test_scenario_4_optical_sar():
    """TEST 4: 'What does SAR show that optical does not?' -> Optical-SAR Agent"""
    plan = QueryPlanner.plan("What does SAR show that optical does not?", image_count=2, has_sar_metadata=True)
    assert not plan.is_ambiguous
    assert plan.selected_agents == [AgentType.OPTICAL_SAR]


def test_scenario_5_area_management():
    """TEST 5: 'What percentage of this area is water?' -> Area Management Agent"""
    plan = QueryPlanner.plan("What percentage of this area is water?", image_count=1)
    assert not plan.is_ambiguous
    assert plan.selected_agents == [AgentType.AREA_MANAGEMENT]
    assert "Area" in plan.intent


def test_scenario_6_rag():
    """TEST 6: 'What is SAR?' -> RAG Agent"""
    plan = QueryPlanner.plan("What is SAR?", image_count=0)
    assert not plan.is_ambiguous
    assert plan.selected_agents == [AgentType.RAG]
    assert "Domain Knowledge" in plan.intent


def test_scenario_7_change_plus_grounding():
    """TEST 7: 'Find new buildings between 2022 and 2026.' -> Change Detection + Grounding"""
    plan = QueryPlanner.plan("Find new buildings between 2022 and 2026.", image_count=2, has_temporal_metadata=True)
    assert not plan.is_ambiguous
    assert AgentType.CHANGE_DETECTION in plan.selected_agents
    assert AgentType.GROUNDING in plan.selected_agents
    assert len(plan.selected_agents) == 2
    # Check dependency execution order: Change Detection first, then Grounding
    assert plan.execution_order == [[AgentType.CHANGE_DETECTION], [AgentType.GROUNDING]]


def test_scenario_8_change_plus_grounding_plus_area():
    """TEST 8: 'Find new buildings between 2022 and 2026 and calculate their affected area.' -> Change + Grounding + Area"""
    plan = QueryPlanner.plan(
        "Find new buildings between 2022 and 2026 and calculate their affected area.",
        image_count=2,
        has_temporal_metadata=True
    )
    assert not plan.is_ambiguous
    assert AgentType.CHANGE_DETECTION in plan.selected_agents
    assert AgentType.GROUNDING in plan.selected_agents
    assert AgentType.AREA_MANAGEMENT in plan.selected_agents
    assert len(plan.selected_agents) == 3


def test_scenario_9_optical_sar_plus_rag():
    """TEST 9: 'Analyze the optical and SAR images and explain why SAR is useful.' -> Optical-SAR + RAG"""
    plan = QueryPlanner.plan(
        "Analyze the optical and SAR images and explain why SAR is useful.",
        image_count=2,
        has_sar_metadata=True
    )
    assert not plan.is_ambiguous
    assert AgentType.OPTICAL_SAR in plan.selected_agents
    assert AgentType.RAG in plan.selected_agents
    assert len(plan.selected_agents) == 2


def test_scenario_10_ambiguity_clarification():
    """TEST 10: 'Analyze this image.' -> Ambiguous / Clarification required"""
    plan = QueryPlanner.plan("Analyze this image.", image_count=1)
    assert plan.is_ambiguous is True
    assert plan.selected_agents == []
    assert plan.clarification_message is not None
    assert "What would you like to analyze" in plan.clarification_message


# =====================================================================
# PART 2: AGENT REGISTRY TESTS
# =====================================================================

def test_agent_registry_metadata():
    """Verifies all 6 agents exist in registry with proper schema definitions."""
    expected_agents = {
        AgentType.VQA,
        AgentType.GROUNDING,
        AgentType.CHANGE_DETECTION,
        AgentType.OPTICAL_SAR,
        AgentType.AREA_MANAGEMENT,
        AgentType.RAG,
    }
    assert set(AGENTS.keys()) == expected_agents
    for ag_type, ag_data in AGENTS.items():
        meta = ag_data["metadata"]
        assert meta.id == ag_type
        assert meta.name
        assert meta.description
        assert len(meta.supported_tasks) > 0
        assert callable(ag_data["adapter"])


# =====================================================================
# PART 3: RESULT AGGREGATION & EVIDENCE PARTITIONING
# =====================================================================

def test_result_aggregator_evidence_partitioning():
    """Verifies IMAGE_EVIDENCE and KNOWLEDGE_EVIDENCE remain strictly partitioned."""
    img_ev = ImageEvidence(type="change_mask", title="Change Mask Overlay", url_or_b64="data:image/png;base64,AAA")
    kn_ev = KnowledgeEvidence(text="SAR penetrates clouds.", source="sar_overview.md", section="Microwave Theory")

    out_change = StandardizedAgentOutput(
        agent=AgentType.CHANGE_DETECTION,
        agent_name="Change Detection Agent",
        answer="Detected 5 changed regions.",
        confidence=0.92,
        image_evidence=[img_ev]
    )
    out_rag = StandardizedAgentOutput(
        agent=AgentType.RAG,
        agent_name="RAG Knowledge Agent",
        answer="SAR uses C-band active microwave radar.",
        confidence=0.88,
        knowledge_evidence=[kn_ev]
    )

    plan = QueryPlanner.plan("Explain what SAR is and show changes.", image_count=2)
    agg = ResultAggregator.aggregate(
        query="Explain what SAR is and show changes.",
        plan=plan,
        agent_outputs=[out_change, out_rag]
    )

    assert len(agg["image_evidence"]) == 1
    assert agg["image_evidence"][0].type == "change_mask"
    assert len(agg["knowledge_evidence"]) == 1
    assert agg["knowledge_evidence"][0].source == "sar_overview.md"
    assert agg["confidence"] == 0.90  # average of 0.92 and 0.88
    assert "Change Detection Agent" in agg["agents_used"]
    assert "RAG Knowledge Agent" in agg["agents_used"]


# =====================================================================
# PART 4: FASTAPI ORCHESTRATOR ENDPOINT TESTS
# =====================================================================

def test_orchestrator_health_endpoint(client):
    """GET /api/orchestrator/health returns 200 and healthy status."""
    res = client.get("/api/orchestrator/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert len(data["registered_agents"]) == 6


def test_orchestrator_agents_endpoint(client):
    """GET /api/orchestrator/agents returns metadata for all 6 agents."""
    res = client.get("/api/orchestrator/agents")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 6
    agent_ids = [a["id"] for a in data["agents"]]
    assert "vqa" in agent_ids
    assert "grounding" in agent_ids
    assert "change_detection" in agent_ids
    assert "optical_sar" in agent_ids
    assert "area_management" in agent_ids
    assert "rag" in agent_ids


def test_orchestrator_ambiguous_query_api(client):
    """POST /api/orchestrator/query returns clarification on ambiguous prompt."""
    res = client.post("/api/orchestrator/query", json={"query": "Analyze this."})
    assert res.status_code == 200
    data = res.json()
    assert data["requires_clarification"] is True
    assert len(data["clarification_options"]) >= 5


def test_orchestrator_area_query_api(client):
    """POST /api/orchestrator/query executes Area Management AI on image."""
    res = client.post(
        "/api/orchestrator/query",
        json={"query": "What percentage of this area is water?", "image_ids": ["bengaluru"]}
    )
    assert res.status_code == 200
    data = res.json()
    assert "Area Management AI" in data["agents_used"]
    assert data["confidence"] is not None
    assert len(data["image_evidence"]) > 0
    assert data["trace"] is not None


def test_orchestrator_custom_base64_image_query(client):
    """Verifies that providing custom Base64 image payload analyzes the uploaded image."""
    import base64
    import io
    from PIL import Image

    # Create synthetic test image (e.g. 100x100 RGB)
    synthetic = Image.new("RGB", (100, 100), color=(34, 139, 34))
    buf = io.BytesIO()
    synthetic.save(buf, format="PNG")
    b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    res = client.post(
        "/api/orchestrator/query",
        json={
            "query": "Calculate land-cover area coverage for this scene",
            "image_b64s": [b64],
            "image_ids": ["user-scene-custom-1"]
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "Area Management AI" in data["agents_used"]
    assert len(data["image_evidence"]) >= 1
    assert data["image_evidence"][0]["url_or_b64"] != ""



def test_orchestrator_alias_endpoint(client):
    """POST /api/query functions identically as primary alias."""
    res = client.post(
        "/api/query",
        json={"query": "What percentage of this area is water?", "image_ids": ["bengaluru"]}
    )
    assert res.status_code == 200
    data = res.json()
    assert "Area Management AI" in data["agents_used"]


# =====================================================================
# PART 5: REGRESSION CHECKS ON EXISTING AGENTS STANDALONE
# =====================================================================

def test_regression_vqa_status_endpoint(client):
    """Verifies existing GET /api/v1/vqa/status is intact."""
    res = client.get("/api/v1/vqa/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert data["model"] == "SatQuery-VQA"


def test_regression_optical_sar_modes_endpoint(client):
    """Verifies existing GET /api/v1/optical-sar/modes is intact."""
    res = client.get("/api/v1/optical-sar/modes")
    assert res.status_code == 200
    modes = res.json()
    assert len(modes) >= 7


def test_regression_rag_status_endpoint(client):
    """Verifies existing GET /api/rag/status is intact."""
    res = client.get("/api/rag/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data


def test_regression_backend_health_check(client):
    """Verifies core GET /health check is intact."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
