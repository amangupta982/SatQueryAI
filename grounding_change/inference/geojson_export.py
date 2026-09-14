"""
GeoJSON Export Engine.
Exports detected change regions to standard RFC 7946 GeoJSON FeatureCollections,
including comprehensive properties (region_id, category, change_type, area, confidence).
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import geojson
from shapely.geometry import Polygon, box, mapping

from ..schemas import ChangeRegion, TemporalChangeScene
from .geospatial import GeospatialLocalizer


class GeoJSONExporter:
    """
    Serializes detected change regions to GeoJSON format.
    """

    @classmethod
    def export_scene_to_geojson(
        cls,
        scene: TemporalChangeScene,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Creates a GeoJSON FeatureCollection from scene regions.
        If geospatial coordinates are missing, uses pixel-coordinate bounding polygons.
        """
        features: List[geojson.Feature] = []
        geo_avail = scene.geospatial.available and scene.geospatial.transform is not None

        for region in scene.regions:
            geom = None
            if geo_avail:
                geom_dict = GeospatialLocalizer.mask_to_wgs84_polygon(region, scene.geospatial)
                if geom_dict:
                    geom = geojson.Polygon(geom_dict["coordinates"])

            if geom is None:
                # Pixel-space polygon: [ [xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax], [xmin, ymin] ]
                xmin, ymin, xmax, ymax = region.bbox
                coords = [[[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax], [xmin, ymin]]]
                geom = geojson.Polygon(coords)

            props = {
                "region_id": region.region_id,
                "category": region.category,
                "change_type": region.change_type,
                "confidence": region.confidence,
                "area_pixels": region.area_pixels,
                "area_m2": region.area_m2,
                "centroid_pixel": region.centroid_pixel,
                "latitude": region.geo.latitude if region.geo else None,
                "longitude": region.geo.longitude if region.geo else None,
                "temporal_t1": scene.temporal.t1_timestamp,
                "temporal_t2": scene.temporal.t2_timestamp,
                "scene_id": scene.scene_id,
            }

            feature = geojson.Feature(geometry=geom, properties=props)
            features.append(feature)

        fc = geojson.FeatureCollection(features)

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                geojson.dump(fc, f, indent=2)

        return fc
