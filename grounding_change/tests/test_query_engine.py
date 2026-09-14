"""
Unit Tests for Query Engine, Natural Language Filtering, and Session Memory.
"""

import pytest
from grounding_change.schemas import (
    ChangeQueryFilter,
    ChangeRegion,
    SceneSummary,
    TemporalChangeScene,
)
from grounding_change.inference.query_engine import ChangeQueryEngine
from grounding_change.inference.session import ChangeSessionManager
from grounding_change.inference.reasoning import ChangeReasoner


@pytest.fixture
def sample_scene():
    r1 = ChangeRegion(
        region_id="R01",
        category="building",
        change_type="added",
        confidence=0.95,
        bbox=[10, 10, 50, 50],
        centroid_pixel=[30, 30],
        area_pixels=1600
    )
    r2 = ChangeRegion(
        region_id="R02",
        category="vegetation",
        change_type="removed",
        confidence=0.88,
        bbox=[60, 60, 100, 100],
        centroid_pixel=[80, 80],
        area_pixels=1600
    )
    r3 = ChangeRegion(
        region_id="R03",
        category="building",
        change_type="added",
        confidence=0.91,
        bbox=[120, 120, 140, 140],
        centroid_pixel=[130, 130],
        area_pixels=400
    )

    summary = SceneSummary(
        change_detected=True,
        total_scene_pixels=40000,
        changed_pixels=3600,
        change_percentage=9.0,
        natural_language_summary="Buildings increased and vegetation decreased."
    )

    return TemporalChangeScene(
        scene_id="sess_test_123",
        summary=summary,
        regions=[r1, r2, r3]
    )


def test_category_filtering(sample_scene):
    q_filter = ChangeQueryFilter(category="building")
    matched = ChangeQueryEngine.filter_regions(sample_scene, q_filter)
    assert len(matched) == 2
    assert all(r.category == "building" for r in matched)


def test_ranking_and_top_k(sample_scene):
    q_filter = ChangeQueryFilter(category="building", rank_by="area", top_k=1)
    matched = ChangeQueryEngine.filter_regions(sample_scene, q_filter)
    assert len(matched) == 1
    assert matched[0].region_id == "R01"  # Largest building


def test_natural_language_query_parsing():
    f1 = ChangeQueryEngine.parse_natural_language_filter("Where were the new buildings?")
    assert f1.category == "building"
    assert f1.change_type == "added"

    f2 = ChangeQueryEngine.parse_natural_language_filter("Show largest change")
    assert f2.rank_by == "area"
    assert f2.top_k == 1


def test_session_memory_and_multi_turn_reasoning(sample_scene):
    mgr = ChangeSessionManager()
    mgr.create_session("sess_test_123", sample_scene)

    # Turn 1: Overview
    ans1 = ChangeReasoner.answer_question(sample_scene, "What changed?", session_id="sess_test_123")
    assert "Buildings increased" in ans1["answer"]

    # Turn 2: Filter buildings
    ans2 = ChangeReasoner.answer_question(sample_scene, "Show only buildings", session_id="sess_test_123")
    assert "2" in ans2["answer"]

    # Turn 3: Coordinates
    ans3 = ChangeReasoner.answer_question(sample_scene, "Give me coordinates", session_id="sess_test_123")
    assert "Pixel" in ans3["answer"] or "Latitude" in ans3["answer"]
