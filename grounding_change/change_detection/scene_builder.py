"""
Temporal Change Scene Builder.
THE CORE ENGINE OF THE GROUNDING_CHANGE SYSTEM.
Transforms raw bitemporal imagery and perception predictions into a
comprehensive, persistent, queryable TemporalChangeScene representation.
Operates fully in Zero-Question Mode.
"""

import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch

from ..config import settings
from ..schemas import (
    CategoryStats,
    ChangeRegion,
    GeoPoint,
    GeoSpatialMetadata,
    SceneSummary,
    SemanticTransition,
    SpectralIndexStats,
    TemporalChangeScene,
    TemporalInfo,
    VisualEvidence,
)
from ..taxonomy import taxonomy
from ..grounding.region_extractor import RegionExtractor
from .statistics import ChangeStatisticsCalculator
from .heatmap import ChangeHeatmapGenerator
from ..preprocessing.spectral import SpectralIndexAnalyzer


class TemporalSceneBuilder:
    """
    Constructs the complete structured change representation for any pair of temporal images.
    """

    def __init__(
        self,
        change_threshold: float = 0.5,
        min_region_area: int = 16,
    ):
        self.change_threshold = change_threshold
        self.region_extractor = RegionExtractor(min_area_pixels=min_region_area)
        self.stats_calculator = ChangeStatisticsCalculator()
        self.heatmap_generator = ChangeHeatmapGenerator()

    def build_scene(
        self,
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        change_probs: np.ndarray,
        sem_t1: np.ndarray,
        sem_t2: np.ndarray,
        scene_id: Optional[str] = None,
        timestamps: Optional[Tuple[str, str]] = None,
        geospatial_meta: Optional[GeoSpatialMetadata] = None,
        spectral_indices: Optional[Dict[str, SpectralIndexStats]] = None,
        feat_diff: Optional[np.ndarray] = None,
    ) -> TemporalChangeScene:
        """
        Builds a comprehensive TemporalChangeScene from input arrays and prediction maps.

        Args:
            img_t1: (H, W, C) or (H, W) uint8 RGB
            img_t2: (H, W, C) or (H, W) uint8 RGB
            change_probs: (H, W) float in [0.0, 1.0]
            sem_t1: (H, W) int taxonomy category IDs for T1
            sem_t2: (H, W) int taxonomy category IDs for T2
            scene_id: Optional identifier (generated if omitted)
            timestamps: Optional (t1_time_str, t2_time_str)
            geospatial_meta: Optional geospatial projection metadata
            spectral_indices: Optional pre-calculated spectral index stats
            feat_diff: Optional feature difference map
        """
        sid = scene_id or f"scene_{uuid.uuid4().hex[:10]}"
        h, w = change_probs.shape[:2]
        total_pixels = h * w

        # 1. Binary change mask by thresholding learned change probability
        change_mask = (change_probs >= self.change_threshold).astype(np.uint8)
        changed_pixels = int(np.sum(change_mask > 0))

        # 2. Extract discrete spatial change regions
        regions = self.region_extractor.extract_regions(
            change_mask=change_mask,
            sem_t1=sem_t1,
            sem_t2=sem_t2,
            confidence_map=change_probs
        )

        change_detected = changed_pixels >= settings.model.min_region_area and len(regions) > 0
        if not change_detected:
            change_mask = np.zeros_like(change_mask)
            changed_pixels = 0
            change_percentage = 0.0
            regions = []
        else:
            change_percentage = round((changed_pixels / total_pixels) * 100.0, 2) if total_pixels > 0 else 0.0

        # 3. If geospatial metadata is present, map pixel centroids/polygons to real-world coordinates
        pix_res = geospatial_meta.pixel_resolution if geospatial_meta else None
        if geospatial_meta and geospatial_meta.available and geospatial_meta.transform:
            self._attach_geographic_coordinates(regions, geospatial_meta)

        # Attach physical areas if resolution is available
        for reg in regions:
            phys = self.stats_calculator.compute_physical_areas(reg.area_pixels, pix_res)
            reg.area_m2 = phys["area_m2"]

        # 4. Compute per-category statistics
        category_stats = self.stats_calculator.compute_category_statistics(
            sem_t1=sem_t1,
            sem_t2=sem_t2,
            change_mask=change_mask,
            regions=regions,
            pixel_resolution=pix_res
        )

        # 5. Compute land-cover transitions
        transitions = self.stats_calculator.compute_transitions(
            sem_t1=sem_t1,
            sem_t2=sem_t2,
            change_mask=change_mask
        )

        # 6. Multispectral indices if not already computed
        if spectral_indices is None:
            spectral_indices = SpectralIndexAnalyzer.compute_all_indices(img_t1, img_t2)

        # 7. Scene Summary & Natural Language Description (Zero-Question Report)
        dominant_cat = None
        max_delta = 0.0
        for cat_name, stats in category_stats.items():
            if abs(stats.change_percent) > abs(max_delta):
                max_delta = stats.change_percent
                dominant_cat = cat_name

        largest_reg_id = regions[0].region_id if regions else None

        nl_report = self._build_natural_language_report(
            change_detected=change_detected,
            changed_pixels=changed_pixels,
            change_percentage=change_percentage,
            category_stats=category_stats,
            regions=regions,
            transitions=transitions,
            timestamps=timestamps
        )

        summary = SceneSummary(
            change_detected=change_detected,
            total_scene_pixels=total_pixels,
            changed_pixels=changed_pixels,
            change_percentage=change_percentage,
            dominant_changed_category=dominant_cat,
            largest_changed_region_id=largest_reg_id,
            natural_language_summary=nl_report
        )

        # 8. Temporal Metadata
        temp_info = TemporalInfo(
            t1_timestamp=timestamps[0] if timestamps else None,
            t2_timestamp=timestamps[1] if timestamps else None
        )

        # 9. Overall Aggregated Statistics
        overall_stats = {
            "total_pixels": total_pixels,
            "changed_pixels": changed_pixels,
            "change_percentage": change_percentage,
            "region_count": len(regions),
            "largest_region_pixels": regions[0].area_pixels if regions else 0,
            "average_region_pixels": round(float(np.mean([r.area_pixels for r in regions])), 1) if regions else 0,
            "physical_area": self.stats_calculator.compute_physical_areas(changed_pixels, pix_res),
            "active_categories": [k for k, v in category_stats.items() if v.regions_changed > 0],
        }

        # 10. Assemble complete representation
        scene = TemporalChangeScene(
            scene_id=sid,
            temporal=temp_info,
            geospatial=geospatial_meta or GeoSpatialMetadata(available=False),
            summary=summary,
            categories=category_stats,
            regions=regions,
            transitions=transitions,
            statistics=overall_stats,
            spectral_indices=spectral_indices,
            visual_evidence=VisualEvidence()
        )

        return scene

    def _attach_geographic_coordinates(self, regions: List[ChangeRegion], geo_meta: GeoSpatialMetadata):
        """Map pixel coordinates to real-world latitude/longitude."""
        try:
            from pyproj import Transformer
            t = geo_meta.transform  # [c, a, b, f, d, e] rasterio affine
            # rasterio Affine: x = c + col*a + row*b; y = f + col*d + row*e
            # or in affine format: x = a*col + b*row + c; y = d*col + e*row + f
            a, b, c, d, e, f = t[0], t[1], t[2], t[3], t[4], t[5]

            transformer = None
            if geo_meta.crs:
                transformer = Transformer.from_crs(geo_meta.crs, "EPSG:4326", always_xy=True)

            for reg in regions:
                col, row = reg.centroid_pixel
                # Affine transform to projected coordinates
                proj_x = a * col + b * row + c
                proj_y = d * col + e * row + f

                lat, lon = None, None
                if transformer:
                    lon, lat = transformer.transform(proj_x, proj_y)
                elif "4326" in str(geo_meta.crs).lower():
                    lon, lat = proj_x, proj_y

                reg.geo = GeoPoint(
                    latitude=round(lat, 6) if lat is not None else None,
                    longitude=round(lon, 6) if lon is not None else None,
                    projected_x=round(proj_x, 3),
                    projected_y=round(proj_y, 3),
                    crs=geo_meta.crs
                )
        except Exception as err:
            print(f"Geospatial transform note: {err}")

    def _build_natural_language_report(
        self,
        change_detected: bool,
        changed_pixels: int,
        change_percentage: float,
        category_stats: Dict[str, CategoryStats],
        regions: List[ChangeRegion],
        transitions: List[SemanticTransition],
        timestamps: Optional[Tuple[str, str]] = None
    ) -> str:
        """Generates comprehensive natural-language scene report."""
        if not change_detected or changed_pixels == 0:
            return "No significant semantic change was detected across the scene."

        time_prefix = ""
        if timestamps and timestamps[0] and timestamps[1]:
            time_prefix = f"Between {timestamps[0]} and {timestamps[1]}: "

        lines = [f"{time_prefix}Comprehensive change analysis detected {change_percentage}% total scene change ({changed_pixels:,} pixels across {len(regions)} localized regions)."]

        # Highlight major category changes
        cat_summaries = []
        for cat_name, stats in category_stats.items():
            if abs(stats.change_percent) >= 0.1 or stats.regions_changed > 0:
                sign = "+" if stats.change_percent > 0 else ""
                cat_summaries.append(f"{cat_name.replace('_', ' ').capitalize()}: {sign}{stats.change_percent}% ({stats.regions_changed} regions)")

        if cat_summaries:
            lines.append("Category Shifts: " + ", ".join(cat_summaries) + ".")

        # Highlight dominant transitions
        if transitions:
            top_t = transitions[:3]
            t_strs = [f"{t.from_category} -> {t.to_category} ({t.percentage}%)" for t in top_t]
            lines.append("Primary Land-Cover Transitions: " + ", ".join(t_strs) + ".")

        if regions:
            r1 = regions[0]
            lines.append(f"Largest change region is {r1.region_id} ({r1.category}, {r1.change_type}, {r1.area_pixels:,} pixels).")

        return " ".join(lines)
