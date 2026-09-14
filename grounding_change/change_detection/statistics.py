"""
Change Statistics and Quantitative Impact Calculator.
Computes scene-level and category-level area deltas, region distributions,
land-cover transitions, and physical area metrics (m², ha, km²).
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from ..schemas import CategoryStats, ChangeRegion, SemanticTransition
from ..taxonomy import taxonomy, ChangeType


class ChangeStatisticsCalculator:
    """
    Analyzes temporal change masks and semantic land-cover maps
    to compute rigorous quantitative statistics.
    """

    @staticmethod
    def compute_category_statistics(
        sem_t1: np.ndarray,
        sem_t2: np.ndarray,
        change_mask: np.ndarray,
        regions: List[ChangeRegion],
        pixel_resolution: Optional[Tuple[float, float]] = None
    ) -> Dict[str, CategoryStats]:
        """
        Computes per-category area percentages, deltas, region counts,
        and directional trends.
        """
        total_pixels = sem_t1.size
        category_stats: Dict[str, CategoryStats] = {}

        for cat in taxonomy.all_categories:
            if cat.id == 0:
                continue  # Skip unclassified background

            cat_id = cat.id
            cat_name = cat.name

            # T1 and T2 pixel counts
            t1_count = int(np.sum(sem_t1 == cat_id))
            t2_count = int(np.sum(sem_t2 == cat_id))

            t1_pct = round((t1_count / total_pixels) * 100.0, 2) if total_pixels > 0 else 0.0
            t2_pct = round((t2_count / total_pixels) * 100.0, 2) if total_pixels > 0 else 0.0
            delta_pct = round(t2_pct - t1_pct, 2)

            if delta_pct > 0.1:
                direction = "increase"
            elif delta_pct < -0.1:
                direction = "decrease"
            else:
                direction = "unchanged"

            # Filter regions for this category
            cat_regions = [r for r in regions if r.category == cat_name]
            regions_changed = len(cat_regions)
            largest_region = max([r.area_pixels for r in cat_regions], default=0)

            # Changed pixels for this category
            changed_for_cat = int(np.sum((change_mask > 0) & ((sem_t1 == cat_id) | (sem_t2 == cat_id))))

            conf = 0.92
            if cat_regions:
                conf = round(float(np.mean([r.confidence for r in cat_regions])), 3)

            category_stats[cat_name] = CategoryStats(
                category=cat_name,
                t1_area_percent=t1_pct,
                t2_area_percent=t2_pct,
                change_percent=delta_pct,
                direction=direction,
                regions_changed=regions_changed,
                largest_region_pixels=largest_region,
                total_changed_pixels=changed_for_cat,
                confidence=conf
            )

        return category_stats

    @staticmethod
    def compute_transitions(
        sem_t1: np.ndarray,
        sem_t2: np.ndarray,
        change_mask: np.ndarray,
        min_pixels: int = 10
    ) -> List[SemanticTransition]:
        """
        Extracts explicit land-cover transitions between T1 and T2.
        Example: vegetation -> building (conversion).
        """
        total_changed = max(int(np.sum(change_mask > 0)), 1)
        transitions: List[SemanticTransition] = []

        changed_idx = np.where(change_mask > 0)
        t1_vals = sem_t1[changed_idx]
        t2_vals = sem_t2[changed_idx]

        # Count (from_id, to_id) pairs
        unique_pairs, counts = np.unique(np.column_stack((t1_vals, t2_vals)), axis=0, return_counts=True)

        for (from_id, to_id), cnt in zip(unique_pairs, counts):
            if cnt < min_pixels:
                continue
            if from_id == to_id and from_id == 0:
                continue

            from_cat = taxonomy.get_by_id(int(from_id)).name
            to_cat = taxonomy.get_by_id(int(to_id)).name

            if from_cat == to_cat:
                ch_type = ChangeType.EXPANDED.value
            elif from_cat in ["bare_land", "background"] and to_cat not in ["bare_land", "background"]:
                ch_type = ChangeType.ADDED.value
            elif from_cat not in ["bare_land", "background"] and to_cat in ["bare_land", "background"]:
                ch_type = ChangeType.REMOVED.value
            else:
                ch_type = ChangeType.CONVERTED.value

            pct = round((cnt / total_changed) * 100.0, 2)

            transitions.append(SemanticTransition(
                from_category=from_cat,
                to_category=to_cat,
                change_type=ch_type,
                pixel_count=int(cnt),
                percentage=pct,
                confidence=0.91
            ))

        # Sort descending by pixel count
        transitions.sort(key=lambda t: t.pixel_count, reverse=True)
        return transitions

    @staticmethod
    def compute_physical_areas(
        pixel_count: int,
        pixel_resolution: Optional[Tuple[float, float]]
    ) -> Dict[str, Optional[float]]:
        """
        Converts pixel counts into physical units (m², hectares, km²)
        ONLY when pixel resolution is explicitly known.
        Never fabricates physical area if resolution is unavailable.
        """
        if not pixel_resolution or pixel_resolution[0] <= 0 or pixel_resolution[1] <= 0:
            return {
                "physical_units_available": False,
                "area_m2": None,
                "area_hectares": None,
                "area_km2": None,
            }

        pixel_area_m2 = abs(pixel_resolution[0] * pixel_resolution[1])
        total_m2 = pixel_count * pixel_area_m2
        total_ha = total_m2 / 10000.0
        total_km2 = total_m2 / 1000000.0

        return {
            "physical_units_available": True,
            "area_m2": round(total_m2, 2),
            "area_hectares": round(total_ha, 4),
            "area_km2": round(total_km2, 6),
            "pixel_size_meters": [abs(pixel_resolution[0]), abs(pixel_resolution[1])]
        }
