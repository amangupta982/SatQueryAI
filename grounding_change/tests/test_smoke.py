"""
End-to-End Smoke Test for Grounding Change Module.
Tests the complete execution chain:
T1 + T2
-> complete analysis
-> change inventory
-> category statistics
-> region localization
-> geospatial conversion
-> visualization
-> JSON
-> follow-up question
"""

import json
from pathlib import Path
import numpy as np
import pytest

from grounding_change.schemas import (
    ChangeAnalysisOutput,
    GeoSpatialMetadata,
)
from grounding_change.inference import (
    analyze_temporal_scene,
    query_temporal_scene,
    session_manager,
)


def test_end_to_end_smoke(tmp_path):
    # 1. Prepare bitemporal satellite imagery pair
    size = 128
    # T1: Baseline scene with background soil and forest
    t1 = np.full((size, size, 3), [70, 140, 70], dtype=np.uint8)
    t1[20:60, 20:60] = [180, 120, 70]  # Bare land patch

    # T2: Later scene with new construction on bare land
    t2 = t1.copy()
    t2[25:55, 25:55] = [230, 50, 50]  # Red building cluster (30x30 = 900 px)

    # Geospatial metadata
    geo_dict = {
        "geospatial_available": True,
        "crs": "EPSG:4326",
        "bounds": [77.5, 12.8, 77.7, 13.0],
        "transform": [0.001, 0.0, 77.5, 0.0, -0.001, 13.0],
        "resolution": [0.001, 0.001]
    }

    session_id = "smoke_session_001"

    # 2. Complete Zero-Question Initial Analysis
    output: ChangeAnalysisOutput = analyze_temporal_scene(
        image_t1=t1,
        image_t2=t2,
        question=None,  # Zero-question mode
        timestamps=("2020-01-01", "2024-01-01"),
        metadata=geo_dict,
        session_id=session_id,
        return_visuals=True,
        return_geo=True
    )

    # 3. Verify Complete Change Inventory & Statistics
    assert output is not None
    assert output.scene_summary is not None
    assert isinstance(output.scene_summary.change_detected, bool)
    assert output.scene_summary.total_scene_pixels == size * size

    # Verify category statistics are populated
    assert isinstance(output.categories, dict)
    assert len(output.categories) > 0
    assert "building" in output.categories
    assert "vegetation" in output.categories

    # Verify discrete regions & spatial localization
    assert isinstance(output.regions, list)
    for r in output.regions:
        assert len(r.bbox) == 4
        assert len(r.centroid_pixel) == 2
        assert r.area_pixels > 0
        assert r.confidence > 0.0
        # Check geospatial coordinate mapping
        if output.geospatial.available:
            assert r.geo is not None
            assert r.geo.latitude is not None
            assert r.geo.longitude is not None

    # Verify visual evidence layers
    assert output.visualizations is not None
    assert output.visualizations.complete_overlay is not None
    assert output.visualizations.heatmap is not None
    assert output.visualizations.legend is not None

    # 4. Verify JSON Serialization Conformance
    json_str = output.model_dump_json()
    parsed_json = json.loads(json_str)
    assert "scene_summary" in parsed_json
    assert "categories" in parsed_json
    assert "regions" in parsed_json
    assert "visualizations" in parsed_json
    assert "confidence" in parsed_json

    # 5. Interactive Follow-up Questioning over Session Memory
    # Follow-up 1: "Where are the new buildings?"
    follow1 = query_temporal_scene(session_id, "Where are the new buildings?")
    assert "answer" in follow1
    assert len(follow1["answer"]) > 0

    # Follow-up 2: "Give me the latitude and longitude."
    follow2 = query_temporal_scene(session_id, "Give me the latitude and longitude.")
    assert "answer" in follow2
    assert "Lat" in follow2["answer"] or "Pixel" in follow2["answer"]

    # Follow-up 3: "Show me everything again."
    follow3 = query_temporal_scene(session_id, "Show me everything again.")
    assert "Restored" in follow3["answer"] or "view" in follow3["answer"]
