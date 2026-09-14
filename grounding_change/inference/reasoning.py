"""
Agent Reasoning Layer for Multitemporal Change Intelligence.
Executes deterministic, evidence-grounded natural language reasoning directly
over the structured TemporalChangeScene and active session memory.
Strictly prevents hallucinations: all numbers, locations, coordinates, and transitions
are derived directly from structured perception representations.
"""

from typing import Any, Dict, List, Optional, Tuple
from ..schemas import ChangeQueryFilter, ChangeRegion, TemporalChangeScene
from ..taxonomy import taxonomy
from .query_engine import ChangeQueryEngine
from .session import SessionState, session_manager


class ChangeReasoner:
    """
    Interprets natural-language user queries, inspects the scene representation,
    executes necessary filtering/aggregations, and constructs factual grounded answers.
    """

    @classmethod
    def answer_question(
        cls,
        scene: TemporalChangeScene,
        question: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main reasoning entry point.
        Returns:
            {
                "answer": str,
                "relevant_regions": List[ChangeRegion],
                "active_filter": ChangeQueryFilter,
                "evidence": Dict[str, Any]
            }
        """
        q = question.lower().strip()
        state: Optional[SessionState] = session_manager.get_session(session_id) if session_id else None

        # 1. "What changed?" / Scene-wide overview
        if q in ["what changed?", "what changed", "summary", "overview", "describe changes"]:
            return {
                "answer": scene.summary.natural_language_summary,
                "relevant_regions": scene.regions,
                "active_filter": ChangeQueryFilter(),
                "evidence": {"total_percentage": scene.summary.change_percentage, "regions": len(scene.regions)}
            }

        # 2. "Show everything again" / Reset filter
        if "everything" in q or "reset" in q or "all changes" in q:
            if state:
                session_manager.update_active_selection(session_id, scene.regions)
            return {
                "answer": f"Restored view to all {len(scene.regions)} detected change regions across the scene.",
                "relevant_regions": scene.regions,
                "active_filter": ChangeQueryFilter(),
                "evidence": {"regions": len(scene.regions)}
            }

        # 3. Coordinate query ("Give me coordinates", "Where are the coordinates?", "lat lon")
        if "coordinate" in q or "lat" in q or "lon" in q:
            target_regions = (state.active_regions if (state and state.active_regions) else None) or scene.regions
            return cls._handle_coordinate_query(target_regions, scene.geospatial)

        # 4. Quantification / "How much" query
        if "how much" in q or "area" in q or "percentage" in q or "quantif" in q:
            return cls._handle_quantification_query(scene, q)

        # 5. Directional / Trend queries ("Did vegetation decrease?", "Did buildings increase?")
        if "did " in q or "increase" in q or "decrease" in q:
            return cls._handle_trend_query(scene, q)

        # 6. Conversion queries ("What was converted into buildings?", "What transformed?")
        if "convert" in q or "transform" in q or "into" in q:
            return cls._handle_conversion_query(scene, q)

        # 7. Disappearance / Removal queries ("What disappeared?", "What was removed?")
        if "disappear" in q or "removed" in q or "lost" in q:
            return cls._handle_removal_query(scene, q)

        # 8. Category / Region-specific filtering ("Where were the new buildings?", "Show only buildings")
        filter_obj = ChangeQueryEngine.parse_natural_language_filter(q)
        matched_regions = ChangeQueryEngine.filter_regions(scene, filter_obj)

        if state:
            session_manager.update_active_selection(
                session_id,
                matched_regions,
                category=filter_obj.category,
                change_type=filter_obj.change_type
            )

        cat_display = filter_obj.category or "detected"
        type_display = f"{filter_obj.change_type} " if filter_obj.change_type else ""

        if not matched_regions:
            answer = f"No {type_display}{cat_display} changes were identified in this scene."
        else:
            total_px = sum(r.area_pixels for r in matched_regions)
            answer = (
                f"Found {len(matched_regions)} {type_display}{cat_display} change region(s) "
                f"encompassing {total_px:,} changed pixels."
            )
            if filter_obj.top_k == 1:
                r0 = matched_regions[0]
                answer = (
                    f"The largest {type_display}{cat_display} region is {r0.region_id}, "
                    f"spanning {r0.area_pixels:,} pixels with confidence {r0.confidence:.2f}."
                )

        return {
            "answer": answer,
            "relevant_regions": matched_regions,
            "active_filter": filter_obj,
            "evidence": {
                "matched_count": len(matched_regions),
                "region_ids": [r.region_id for r in matched_regions[:10]]
            }
        }

    @classmethod
    def _handle_coordinate_query(cls, regions: List[ChangeRegion], geo_meta) -> Dict[str, Any]:
        if not geo_meta.available:
            coords = [f"{r.region_id}: Pixel [{r.centroid_pixel[0]}, {r.centroid_pixel[1]}]" for r in regions[:8]]
            return {
                "answer": (
                    f"Real-world geospatial coordinates are unavailable for this scene (missing CRS/Transform metadata). "
                    f"Returning image-pixel locations: {'; '.join(coords)}."
                ),
                "relevant_regions": regions,
                "active_filter": ChangeQueryFilter(),
                "evidence": {"geospatial_available": False, "pixel_coordinates": [r.centroid_pixel for r in regions]}
            }

        geo_coords = []
        for r in regions[:8]:
            if r.geo and r.geo.latitude is not None and r.geo.longitude is not None:
                geo_coords.append(f"{r.region_id} ({r.category}): Lat {r.geo.latitude:.5f}, Lon {r.geo.longitude:.5f}")

        if geo_coords:
            ans = f"Geographic coordinates for active change regions: {'; '.join(geo_coords)}."
        else:
            coords = [f"{r.region_id}: Pixel [{r.centroid_pixel[0]}, {r.centroid_pixel[1]}]" for r in regions[:8]]
            ans = f"Geospatial coordinates could not be computed for the selected regions. Returning Pixel locations: {'; '.join(coords)}."

        return {
            "answer": ans,
            "relevant_regions": regions,
            "active_filter": ChangeQueryFilter(),
            "evidence": {"geospatial_available": True, "coordinates": geo_coords}
        }

    @classmethod
    def _handle_quantification_query(cls, scene: TemporalChangeScene, q: str) -> Dict[str, Any]:
        matched_cat = taxonomy.match_category(q)
        if matched_cat and matched_cat.id > 0:
            stats = scene.categories.get(matched_cat.name)
            if stats:
                sign = "+" if stats.change_percent > 0 else ""
                ans = (
                    f"{matched_cat.display_name} shifted by {sign}{stats.change_percent}% "
                    f"(from {stats.t1_area_percent}% to {stats.t2_area_percent}% of total scene area) "
                    f"across {stats.regions_changed} localized regions."
                )
                cat_regions = [r for r in scene.regions if r.category == matched_cat.name]
                return {
                    "answer": ans,
                    "relevant_regions": cat_regions,
                    "active_filter": ChangeQueryFilter(category=matched_cat.name),
                    "evidence": stats.model_dump()
                }

        # Overall scene quantification
        phys = scene.statistics.get("physical_area", {})
        m2_str = f" ({phys.get('area_m2'):,} m²)" if phys.get("physical_units_available") and phys.get("area_m2") else ""
        ans = (
            f"A total of {scene.summary.changed_pixels:,} pixels{m2_str} changed between T1 and T2, "
            f"accounting for {scene.summary.change_percentage}% of the scene."
        )
        return {
            "answer": ans,
            "relevant_regions": scene.regions,
            "active_filter": ChangeQueryFilter(),
            "evidence": scene.summary.model_dump()
        }

    @classmethod
    def _handle_trend_query(cls, scene: TemporalChangeScene, q: str) -> Dict[str, Any]:
        matched_cat = taxonomy.match_category(q)
        if matched_cat and matched_cat.id > 0:
            stats = scene.categories.get(matched_cat.name)
            if stats:
                if stats.direction == "increase":
                    ans = f"Yes, {matched_cat.display_name} increased by {stats.change_percent}% across {stats.regions_changed} regions."
                elif stats.direction == "decrease":
                    ans = f"Yes, {matched_cat.display_name} decreased by {abs(stats.change_percent)}% (overall shift: {stats.change_percent}%)."
                else:
                    ans = f"No significant change was observed in {matched_cat.display_name} (net shift {stats.change_percent}%)."

                cat_regions = [r for r in scene.regions if r.category == matched_cat.name]
                return {
                    "answer": ans,
                    "relevant_regions": cat_regions,
                    "active_filter": ChangeQueryFilter(category=matched_cat.name),
                    "evidence": stats.model_dump()
                }

        return {
            "answer": scene.summary.natural_language_summary,
            "relevant_regions": scene.regions,
            "active_filter": ChangeQueryFilter(),
            "evidence": {}
        }

    @classmethod
    def _handle_conversion_query(cls, scene: TemporalChangeScene, q: str) -> Dict[str, Any]:
        matched_cat = taxonomy.match_category(q)
        target_name = matched_cat.name if matched_cat else None

        relevant_transitions = []
        for t in scene.transitions:
            if target_name and t.to_category == target_name:
                relevant_transitions.append(t)
            elif not target_name and t.change_type == "converted":
                relevant_transitions.append(t)

        if not relevant_transitions:
            ans = f"No conversion transitions leading to {target_name or 'new classes'} were detected."
        else:
            t_strs = [f"{t.from_category} -> {t.to_category} ({t.pixel_count:,} pixels, {t.percentage}%)" for t in relevant_transitions]
            ans = f"Detected land-cover transitions: {'; '.join(t_strs)}."

        return {
            "answer": ans,
            "relevant_regions": scene.regions,
            "active_filter": ChangeQueryFilter(category=target_name, change_type="converted"),
            "evidence": {"transitions": [t.model_dump() for t in relevant_transitions]}
        }

    @classmethod
    def _handle_removal_query(cls, scene: TemporalChangeScene, q: str) -> Dict[str, Any]:
        removed_regions = [r for r in scene.regions if r.change_type in ["removed", "reduced"]]
        matched_cat = taxonomy.match_category(q)
        if matched_cat:
            removed_regions = [r for r in removed_regions if r.category == matched_cat.name]

        if not removed_regions:
            ans = "No significant removals or demolitions were detected in this scene."
        else:
            total_px = sum(r.area_pixels for r in removed_regions)
            ans = f"Identified {len(removed_regions)} removal/reduction region(s) totaling {total_px:,} pixels."

        return {
            "answer": ans,
            "relevant_regions": removed_regions,
            "active_filter": ChangeQueryFilter(change_type="removed"),
            "evidence": {"removed_count": len(removed_regions)}
        }
