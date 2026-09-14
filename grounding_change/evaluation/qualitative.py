"""
Qualitative Evaluation Panel Generator.
Generates multi-panel qualitative benchmark comparisons:
  T1 | T2 | Difference | Change Map | Semantic Map | Grounding
across 5 required scenarios:
1. Building Change (New construction)
2. Vegetation Change (Deforestation / Loss)
3. Water Change (Reservoir expansion / Flooding)
4. No-Change (Identical scene with seasonal/illumination variance)
5. Mixed-Category Change (Urban expansion + vegetation loss)
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..config import settings, OUTPUT_DIR
from ..taxonomy import taxonomy
from ..inference.pipeline import ChangeInferencePipeline


class QualitativeBenchmarkGenerator:
    """
    Constructs standardized 6-panel qualitative evaluation strips.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir or (OUTPUT_DIR / "qualitative_evaluation"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline = ChangeInferencePipeline()

    def generate_synthetic_scenario(self, scenario_type: str) -> Tuple[np.ndarray, np.ndarray, str]:
        """
        Creates synthetic bitemporal satellite image pairs mimicking remote-sensing phenomena.
        """
        size = 256
        # Base scene: green vegetation with background soil
        t1 = np.full((size, size, 3), [60, 140, 60], dtype=np.uint8)
        # Add some ground texture
        t1[150:220, 20:100] = [160, 110, 60]  # bare soil
        t2 = t1.copy()

        question = "What changed in this scene?"

        if scenario_type == "building_change":
            # New buildings appear on bare ground
            t2[160:200, 30:80] = [220, 60, 60]  # red building roofs
            question = "Where are the new buildings?"

        elif scenario_type == "vegetation_change":
            # Forest clearing / deforestation
            t2[30:110, 120:200] = [170, 120, 70]  # cleared bare soil
            question = "How much vegetation was lost?"

        elif scenario_type == "water_change":
            # Water body / pond expands
            t1[50:100, 50:100] = [30, 90, 180]  # original small pond
            t2[40:130, 40:140] = [30, 90, 180]  # flooded/expanded pond
            question = "Did water increase?"

        elif scenario_type == "no_change":
            # Only slight illumination noise, no physical semantic change
            noise = np.random.randint(-5, 5, size=(size, size, 3), dtype=np.int16)
            t2 = np.clip(t1.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            question = "What changed?"

        elif scenario_type == "mixed_category":
            # Both building additions and vegetation loss
            t2[160:200, 30:80] = [220, 60, 60]  # buildings
            t2[30:90, 140:200] = [170, 120, 70]  # deforestation
            question = "What categories changed?"

        return t1, t2, question

    def create_comparison_strip(self, scenario_type: str) -> Path:
        """
        Runs pipeline on scenario and stitches a 6-panel composite image:
        T1 | T2 | Difference | Change Map | Semantic Map | Grounding
        """
        t1, t2, query = self.generate_synthetic_scenario(scenario_type)
        output = self.pipeline.analyze(t1, t2, question=query, session_id=f"qual_{scenario_type}")

        h, w = t1.shape[:2]
        pad = 4
        panel_w = w
        panel_h = h + 28  # With title header

        # 6 panels:
        # 1. T1
        # 2. T2
        # 3. Difference
        g1 = cv2.cvtColor(t1, cv2.COLOR_RGB2GRAY)
        g2 = cv2.cvtColor(t2, cv2.COLOR_RGB2GRAY)
        diff_raw = cv2.applyColorMap(cv2.absdiff(g2, g1), cv2.COLORMAP_VIRIDIS)
        diff_rgb = cv2.cvtColor(diff_raw, cv2.COLOR_BGR2RGB)

        # 4. Change Map
        change_mask = (t2 != t1).any(axis=-1).astype(np.uint8) * 255
        change_rgb = np.stack([change_mask] * 3, axis=-1)

        # 5. Semantic Map
        sem_map = np.zeros_like(t2)
        for r in output.regions:
            xmin, ymin, xmax, ymax = r.bbox
            cat_def = taxonomy.get_by_name(r.category)
            color = cat_def.color_rgb if cat_def else (255, 0, 0)
            sem_map[ymin:ymax, xmin:xmax] = color

        # 6. Grounding Overlay
        grounding_overlay = t2.copy()
        for r in output.regions:
            xmin, ymin, xmax, ymax = r.bbox
            cv2.rectangle(grounding_overlay, (xmin, ymin), (xmax, ymax), (0, 255, 255), 2)
            cv2.circle(grounding_overlay, tuple(r.centroid_pixel), 4, (0, 0, 255), -1)

        panels = [
            ("T1 (Earlier)", t1),
            ("T2 (Later)", t2),
            ("Difference", diff_rgb),
            ("Change Map", change_rgb),
            ("Semantic Map", sem_map),
            ("Grounding", grounding_overlay),
        ]

        # Assemble horizontal strip
        strip_w = len(panels) * (panel_w + pad) + pad
        strip_h = panel_h + pad * 2

        composite = Image.new("RGB", (strip_w, strip_h), color=(240, 243, 241))
        draw = ImageDraw.Draw(composite)

        x_offset = pad
        for title, img_arr in panels:
            # Draw header title
            draw.text((x_offset + 4, pad + 4), title, fill=(22, 39, 33))

            # Paste image
            p_img = Image.fromarray(img_arr)
            composite.paste(p_img, (x_offset, pad + 24))
            x_offset += panel_w + pad

        out_path = self.output_dir / f"qualitative_{scenario_type}.png"
        composite.save(out_path)
        print(f"Saved qualitative evaluation strip to {out_path}")
        return out_path

    def run_all_scenarios(self) -> List[Path]:
        """Runs qualitative evaluations across all 5 required domains."""
        scenarios = [
            "building_change",
            "vegetation_change",
            "water_change",
            "no_change",
            "mixed_category",
        ]
        paths = []
        for s in scenarios:
            paths.append(self.create_comparison_strip(s))
        return paths
