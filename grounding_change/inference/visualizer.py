"""
Change Visualizer & Multi-Layer Evidence Renderer.
Generates comprehensive visualization layers:
- Original T1 & T2
- Simple difference image
- Continuous change heatmap
- Binary change mask
- Semantic land-cover map
- Complete multi-category change overlay
- Category-specific toggleable overlays (buildings, vegetation, water, etc.)
- Bounding-box and centroid overlays with confidence tags
- Query-specific highlighted visualization
- Machine-readable legend metadata
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..config import OUTPUT_DIR, PROJECT_ROOT, settings
from ..schemas import ChangeRegion, TemporalChangeScene, VisualEvidence
from ..taxonomy import taxonomy
from ..change_detection.heatmap import ChangeHeatmapGenerator


class ChangeVisualizer:
    """
    Renders visual evidence images and manages toggleable layer metadata for the frontend.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir or (OUTPUT_DIR / "evidence"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_visualizations(
        self,
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        change_mask: np.ndarray,
        sem_t1: np.ndarray,
        sem_t2: np.ndarray,
        scene: TemporalChangeScene,
        heatmap_intensity: Optional[np.ndarray] = None,
        query_regions: Optional[List[ChangeRegion]] = None,
    ) -> VisualEvidence:
        """
        Generates every required visual evidence layer on disk and returns the VisualEvidence schema.
        """
        sid = scene.scene_id
        h, w = img_t1.shape[:2]

        # 1. T1 and T2 original images
        t1_filename = f"{sid}_t1.png"
        t2_filename = f"{sid}_t2.png"
        self._save_image(img_t1, self.output_dir / t1_filename)
        self._save_image(img_t2, self.output_dir / t2_filename)

        # 2. Simple temporal difference image
        g1 = cv2.cvtColor(img_t1, cv2.COLOR_RGB2GRAY) if img_t1.ndim == 3 else img_t1
        g2 = cv2.cvtColor(img_t2, cv2.COLOR_RGB2GRAY) if img_t2.ndim == 3 else img_t2
        diff_raw = cv2.absdiff(g2, g1)
        diff_color = cv2.applyColorMap(diff_raw, cv2.COLORMAP_VIRIDIS)
        diff_rgb = cv2.cvtColor(diff_color, cv2.COLOR_BGR2RGB)
        diff_filename = f"{sid}_difference.png"
        self._save_image(diff_rgb, self.output_dir / diff_filename)

        # 3. Continuous change heatmap
        if heatmap_intensity is None:
            heat_dict = ChangeHeatmapGenerator.generate_heatmap(img_t1, img_t2)
            heatmap_intensity = heat_dict["composite_heatmap"]
        heatmap_color = ChangeHeatmapGenerator.render_color_heatmap(heatmap_intensity)
        # Blend with T2
        heatmap_overlay = cv2.addWeighted(img_t2, 0.4, heatmap_color, 0.6, 0)
        heatmap_filename = f"{sid}_heatmap.png"
        self._save_image(heatmap_overlay, self.output_dir / heatmap_filename)

        # 4. Binary change mask (White on Black)
        mask_binary = (change_mask > 0).astype(np.uint8) * 255
        mask_filename = f"{sid}_binary_mask.png"
        self._save_image(mask_binary, self.output_dir / mask_filename)

        # 5. Semantic change map (Colored by destination land cover where change occurred)
        semantic_map = self._render_semantic_map(sem_t2, change_mask)
        sem_filename = f"{sid}_semantic_map.png"
        self._save_image(semantic_map, self.output_dir / sem_filename)

        # 6. Complete change overlay (All categories blended onto T2 with bounding boxes and centroids)
        complete_overlay = self._render_complete_overlay(img_t2, change_mask, sem_t2, scene.regions)
        complete_filename = f"{sid}_complete_overlay.png"
        self._save_image(complete_overlay, self.output_dir / complete_filename)

        # 7. Category-specific overlays
        cat_overlays: Dict[str, str] = {}
        for cat in taxonomy.all_categories:
            if cat.id == 0:
                continue
            cat_mask = (change_mask > 0) & (sem_t2 == cat.id)
            if np.any(cat_mask):
                cat_img = self._render_single_category_overlay(img_t2, cat_mask, cat, scene.regions)
                cat_file = f"{sid}_overlay_{cat.name}.png"
                self._save_image(cat_img, self.output_dir / cat_file)
                cat_overlays[cat.name] = cat_file

        # 8. Query-specific visualization (if query_regions supplied)
        query_filename = None
        if query_regions is not None:
            query_img = self._render_query_overlay(img_t2, query_regions)
            query_filename = f"{sid}_query_highlight.png"
            self._save_image(query_img, self.output_dir / query_filename)

        # 9. Build Legend Metadata
        legend = self._build_legend_metadata(scene.regions)

        evidence = VisualEvidence(
            t1_image=t1_filename,
            t2_image=t2_filename,
            difference_image=diff_filename,
            heatmap=heatmap_filename,
            change_mask=mask_filename,
            semantic_change_map=sem_filename,
            complete_overlay=complete_filename,
            category_overlays=cat_overlays,
            query_visualization=query_filename,
            legend=legend
        )
        return evidence

    def _render_semantic_map(self, sem_map: np.ndarray, change_mask: np.ndarray) -> np.ndarray:
        """Color-coded semantic classification map."""
        h, w = sem_map.shape[:2]
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

        for cat in taxonomy.all_categories:
            if cat.id == 0:
                continue
            mask = (sem_map == cat.id) & (change_mask > 0)
            canvas[mask] = cat.color_rgb

        return canvas

    def _render_complete_overlay(
        self,
        base_img: np.ndarray,
        change_mask: np.ndarray,
        sem_t2: np.ndarray,
        regions: List[ChangeRegion]
    ) -> np.ndarray:
        """Composite overlay with colored masks, bounding boxes, and centroid markers."""
        overlay = base_img.copy()

        # Fill changed pixels by category color
        for cat in taxonomy.all_categories:
            if cat.id == 0:
                continue
            cat_mask = (change_mask > 0) & (sem_t2 == cat.id)
            if np.any(cat_mask):
                overlay[cat_mask] = cat.color_rgb

        blended = cv2.addWeighted(overlay, 0.45, base_img, 0.55, 0)

        # Draw bounding boxes and centroids for top regions
        for r in regions[:15]:
            x_min, y_min, x_max, y_max = r.bbox
            cat_def = taxonomy.get_by_name(r.category)
            color_bgr = tuple(reversed(cat_def.color_rgb)) if cat_def else (0, 0, 255)

            # Bounding box
            cv2.rectangle(blended, (x_min, y_min), (x_max, y_max), color_bgr, 2)

            # Centroid point
            c_x, c_y = r.centroid_pixel
            cv2.circle(blended, (c_x, c_y), 4, (255, 255, 255), -1)
            cv2.circle(blended, (c_x, c_y), 2, color_bgr, -1)

            # Label tag
            label_txt = f"{r.region_id}:{r.category[:4]} ({r.confidence:.2f})"
            cv2.putText(blended, label_txt, (x_min, max(12, y_min - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

        return blended

    def _render_single_category_overlay(
        self,
        base_img: np.ndarray,
        cat_mask: np.ndarray,
        cat,
        regions: List[ChangeRegion]
    ) -> np.ndarray:
        """Overlay focused exclusively on a single semantic category."""
        overlay = base_img.copy()
        overlay[cat_mask] = cat.color_rgb
        blended = cv2.addWeighted(overlay, 0.5, base_img, 0.5, 0)

        # Draw boxes for this category
        cat_regions = [r for r in regions if r.category == cat.name]
        color_bgr = tuple(reversed(cat.color_rgb))
        for r in cat_regions:
            x_min, y_min, x_max, y_max = r.bbox
            cv2.rectangle(blended, (x_min, y_min), (x_max, y_max), color_bgr, 2)
            c_x, c_y = r.centroid_pixel
            cv2.circle(blended, (c_x, c_y), 3, (255, 255, 255), -1)

        return blended

    def _render_query_overlay(self, base_img: np.ndarray, query_regions: List[ChangeRegion]) -> np.ndarray:
        """Highlights only query-relevant filtered regions with a distinctive amber glow."""
        blended = base_img.copy()
        glow_mask = np.zeros(base_img.shape[:2], dtype=np.uint8)

        for r in query_regions:
            x_min, y_min, x_max, y_max = r.bbox
            # Bright highlighted box
            cv2.rectangle(blended, (x_min, y_min), (x_max, y_max), (0, 255, 255), 3)
            # Centroid
            c_x, c_y = r.centroid_pixel
            cv2.circle(blended, (c_x, c_y), 5, (0, 0, 255), -1)
            cv2.putText(blended, f"{r.region_id} ({r.category})", (x_min, max(15, y_min - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 2)

        return blended

    def _build_legend_metadata(self, regions: List[ChangeRegion]) -> Dict[str, Any]:
        """Builds machine-readable legend for frontend rendering."""
        cats_present = set(r.category for r in regions)
        legend_items = []

        for cat in taxonomy.all_categories:
            if cat.id == 0:
                continue
            legend_items.append({
                "category": cat.name,
                "display_name": cat.display_name,
                "color_rgb": cat.color_rgb,
                "color_hex": cat.color_hex,
                "present_in_scene": cat.name in cats_present,
                "description": cat.description
            })

        return {
            "categories": legend_items,
            "change_types": {
                "added": "New feature constructed or appeared",
                "removed": "Feature demolished, cleared, or disappeared",
                "expanded": "Existing feature enlarged in surface area",
                "reduced": "Existing feature shrunk in surface area",
                "converted": "Land cover transformed from one type into another"
            },
            "visual_conventions": {
                "boxes": "Discrete detected change object boundaries",
                "dots": "Centroid center of mass for changed region",
                "heatmap": "Continuous intensity gradient from blue (low) to red (high change)"
            }
        }

    def _save_image(self, arr: np.ndarray, path: Path):
        """Save array to disk via PIL or OpenCV."""
        path.parent.mkdir(parents=True, exist_ok=True)
        if arr.ndim == 2:
            Image.fromarray(arr).save(path)
        else:
            Image.fromarray(arr.astype(np.uint8)).save(path)
