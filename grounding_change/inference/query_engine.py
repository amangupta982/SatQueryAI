"""
Query Filtering and Spatial Ranking Engine.
Filters and sorts the structured TemporalChangeScene regions by category,
change type, confidence, physical area, geographic coordinates, and rankings.
"""

from typing import List, Optional
from ..schemas import ChangeQueryFilter, ChangeRegion, TemporalChangeScene
from ..taxonomy import taxonomy


class ChangeQueryEngine:
    """
    Executes structured filters and ranking operations over ChangeRegion collections.
    """

    @classmethod
    def filter_regions(
        cls,
        scene: TemporalChangeScene,
        query_filter: ChangeQueryFilter
    ) -> List[ChangeRegion]:
        """
        Applies filter criteria to scene regions.
        """
        results = list(scene.regions)

        # 1. Filter by category
        if query_filter.category:
            target_cat = query_filter.category.lower().strip()
            # Resolve aliases
            cat_def = taxonomy.get_by_name(target_cat)
            resolved_name = cat_def.name if cat_def else target_cat
            results = [r for r in results if r.category.lower() == resolved_name]

        # 2. Filter by change type (added, removed, expanded, etc.)
        if query_filter.change_type:
            target_type = query_filter.change_type.lower().strip()
            results = [r for r in results if r.change_type.lower() == target_type]

        # 3. Filter by minimum confidence
        if query_filter.confidence_min is not None:
            results = [r for r in results if r.confidence >= query_filter.confidence_min]

        # 4. Filter by minimum pixel area
        if query_filter.area_min_pixels is not None:
            results = [r for r in results if r.area_pixels >= query_filter.area_min_pixels]

        # 5. Filter by minimum physical area (m²)
        if query_filter.area_min_m2 is not None:
            results = [r for r in results if r.area_m2 is not None and r.area_m2 >= query_filter.area_min_m2]

        # 6. Filter by geographic bounding box [min_lon, min_lat, max_lon, max_lat]
        if query_filter.geographic_bounds and len(query_filter.geographic_bounds) == 4:
            min_x, min_y, max_x, max_y = query_filter.geographic_bounds
            filtered_geo = []
            for r in results:
                if r.geo and r.geo.longitude is not None and r.geo.latitude is not None:
                    if (min_x <= r.geo.longitude <= max_x) and (min_y <= r.geo.latitude <= max_y):
                        filtered_geo.append(r)
            results = filtered_geo

        # 7. Spatial Ranking
        if query_filter.rank_by:
            rank = query_filter.rank_by.lower()
            if "area" in rank:
                results.sort(key=lambda r: r.area_pixels, reverse=True)
            elif "conf" in rank:
                results.sort(key=lambda r: r.confidence, reverse=True)
            elif "intensity" in rank or "significan" in rank:
                # Weighted combination of area and confidence
                results.sort(key=lambda r: r.area_pixels * r.confidence, reverse=True)

        # 8. Top K selection
        if query_filter.top_k is not None and query_filter.top_k > 0:
            results = results[:query_filter.top_k]

        return results

    @classmethod
    def parse_natural_language_filter(cls, query: str) -> ChangeQueryFilter:
        """
        Parses user question text into a structured ChangeQueryFilter.
        Example: 'Show top 5 building changes larger than 500 pixels'
        """
        q = query.lower()
        f = ChangeQueryFilter()

        # Category detection
        matched_cat = taxonomy.match_category(q)
        if matched_cat and matched_cat.id > 0:
            f.category = matched_cat.name

        # Change type detection
        for ch_type in ["added", "new", "constructed"]:
            if ch_type in q:
                f.change_type = "added"
                break
        for ch_type in ["removed", "demolished", "lost", "disappeared"]:
            if ch_type in q:
                f.change_type = "removed"
                break
        if "expanded" in q or "expansion" in q or "growth" in q:
            f.change_type = "expanded"
        if "converted" in q or "transition" in q:
            f.change_type = "converted"

        # Ranking keywords
        if "largest" in q or "biggest" in q or "most extensive" in q:
            f.rank_by = "area"
            f.top_k = 1
        elif "top 3" in q:
            f.top_k = 3
            f.rank_by = "area"
        elif "top 5" in q:
            f.top_k = 5
            f.rank_by = "area"
        elif "highest confidence" in q:
            f.rank_by = "confidence"

        # Confidence filter
        if "high confidence" in q:
            f.confidence_min = 0.85

        return f
