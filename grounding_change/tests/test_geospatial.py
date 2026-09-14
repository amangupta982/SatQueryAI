"""
Unit Tests for Geospatial Localization & GeoJSON Export.
"""

from pathlib import Path
import numpy as np
import pytest
import geojson

from grounding_change.schemas import (
    ChangeRegion,
    GeoSpatialMetadata,
    SceneSummary,
    TemporalChangeScene,
)
from grounding_change.inference.geospatial import GeospatialLocalizer
from grounding_change.inference.geojson_export import GeoJSONExporter


def test_pixel_to_projected_and_latlon():
    # Affine transform: x = 500000 + col*10, y = 6000000 - row*10 (UTM Zone 32N EPSG:32632)
    transform = [10.0, 0.0, 500000.0, 0.0, -10.0, 6000000.0]
    crs = "EPSG:32632"

    px_x, px_y = GeospatialLocalizer.pixel_to_projected(100, 200, transform)
    assert px_x == 501000.0
    assert px_y == 5998000.0

    lat, lon = GeospatialLocalizer.projected_to_latlon(px_x, px_y, crs)
    assert lat is not None and lon is not None
    assert 53.0 <= lat <= 55.0  # In UTM 32N European latitude range


def test_missing_geospatial_metadata_no_fabrication():
    # Empty/missing metadata
    geo_meta = GeoSpatialMetadata(available=False)
    loc = GeospatialLocalizer.localize_bounding_box([10, 20, 50, 60], geo_meta)

    assert loc["geospatial_available"] is False
    assert loc["coordinate_type"] == "image_pixel"
    assert "latlon_bounds" not in loc or loc.get("latlon_bounds") is None


def test_geojson_export(tmp_path):
    geo_meta = GeoSpatialMetadata(
        available=True,
        crs="EPSG:4326",
        transform=[0.001, 0.0, 77.0, 0.0, -0.001, 13.0]
    )

    region = ChangeRegion(
        region_id="R01",
        category="building",
        change_type="added",
        confidence=0.95,
        bbox=[10, 10, 40, 40],
        centroid_pixel=[25, 25],
        area_pixels=900
    )

    summary = SceneSummary(
        change_detected=True,
        total_scene_pixels=10000,
        changed_pixels=900,
        change_percentage=9.0
    )

    scene = TemporalChangeScene(
        scene_id="test_geo_scene",
        geospatial=geo_meta,
        summary=summary,
        regions=[region]
    )

    out_file = tmp_path / "test_changes.geojson"
    fc = GeoJSONExporter.export_scene_to_geojson(scene, output_path=out_file)

    assert len(fc["features"]) == 1
    feat = fc["features"][0]
    assert feat["properties"]["region_id"] == "R01"
    assert feat["properties"]["category"] == "building"
    assert out_file.exists()
