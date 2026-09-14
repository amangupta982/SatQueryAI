"""
Geospatial Localization Engine.
Translates pixel coordinates and regions into projected coordinates and WGS84 Lat/Lon.
Extracts geographic polygons from pixel masks.
Strictly avoids coordinate fabrication when metadata is missing.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from shapely.geometry import Polygon, mapping, box
from pyproj import Transformer

from ..schemas import BoundingBox, ChangeRegion, GeoPoint, GeoSpatialMetadata


class GeospatialLocalizer:
    """
    Transforms pixel locations to projected coordinates and standard WGS84 (EPSG:4326) Lat/Lon.
    """

    @staticmethod
    def pixel_to_projected(col: float, row: float, transform: List[float]) -> Tuple[float, float]:
        """
        Affine transform from pixel (col, row) to projected (x, y).
        Standard 6-element GDAL/rasterio transform:
        x = c + col*a + row*b
        y = f + col*d + row*e
        """
        a, b, c, d, e, f = transform[0], transform[1], transform[2], transform[3], transform[4], transform[5]
        x = a * col + b * row + c
        y = d * col + e * row + f
        return x, y

    @staticmethod
    def projected_to_latlon(proj_x: float, proj_y: float, crs_str: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Reprojects projected coordinates (e.g. UTM, WebMercator) to WGS84 Lat/Lon.
        """
        if not crs_str:
            return None, None
        try:
            transformer = Transformer.from_crs(crs_str, "EPSG:4326", always_xy=True)
            lon, lat = transformer.transform(proj_x, proj_y)
            return round(lat, 6), round(lon, 6)
        except Exception:
            if "4326" in crs_str.lower():
                return round(proj_y, 6), round(proj_x, 6)
            return None, None

    @classmethod
    def localize_bounding_box(
        cls,
        bbox: List[int],
        geo_meta: GeoSpatialMetadata
    ) -> Dict[str, Any]:
        """
        Calculates real-world bounds and geometry for a pixel bounding box [x_min, y_min, x_max, y_max].
        """
        if not geo_meta.available or not geo_meta.transform:
            return {
                "coordinate_type": "image_pixel",
                "geospatial_available": False,
                "pixel_bbox": bbox
            }

        x_min, y_min, x_max, y_max = bbox
        p1_x, p1_y = cls.pixel_to_projected(x_min, y_min, geo_meta.transform)
        p2_x, p2_y = cls.pixel_to_projected(x_max, y_max, geo_meta.transform)

        min_x = min(p1_x, p2_x)
        max_x = max(p1_x, p2_x)
        min_y = min(p1_y, p2_y)
        max_y = max(p1_y, p2_y)

        poly_proj = box(min_x, min_y, max_x, max_y)

        # Reproject corners to WGS84
        lat_min, lon_min = cls.projected_to_latlon(min_x, min_y, geo_meta.crs or "")
        lat_max, lon_max = cls.projected_to_latlon(max_x, max_y, geo_meta.crs or "")

        wgs84_box = None
        if lat_min is not None and lon_min is not None and lat_max is not None and lon_max is not None:
            wgs84_box = box(min(lon_min, lon_max), min(lat_min, lat_max), max(lon_min, lon_max), max(lat_min, lat_max))

        return {
            "coordinate_type": "geographic",
            "geospatial_available": True,
            "crs": geo_meta.crs,
            "projected_bounds": [min_x, min_y, max_x, max_y],
            "latlon_bounds": [min(lat_min, lat_max), min(lon_min, lon_max), max(lat_min, lat_max), max(lon_min, lon_max)] if lat_min else None,
            "projected_polygon": mapping(poly_proj),
            "wgs84_polygon": mapping(wgs84_box) if wgs84_box else None,
        }

    @classmethod
    def mask_to_wgs84_polygon(
        cls,
        region: ChangeRegion,
        geo_meta: GeoSpatialMetadata
    ) -> Optional[Dict[str, Any]]:
        """
        Generates GeoJSON-compatible Polygon geometry for a detected region.
        """
        if not geo_meta.available or not geo_meta.transform:
            return None

        # Fallback to bounding box polygon
        loc = cls.localize_bounding_box(region.bbox, geo_meta)
        return loc.get("wgs84_polygon")
