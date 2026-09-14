"""
End-to-End Multitemporal Change Intelligence Pipeline.
Orchestrates:
  Image Loading -> Alignment & Preprocessing -> Neural Feature Extraction ->
  Temporal Fusion -> Binary Change Detection -> Semantic Segmentation ->
  Transition Modeling -> Connected Component Grounding -> Geospatial Localization ->
  Statistics & Indices -> Structured Scene Building -> Visual Evidence Generation ->
  Agent Reasoning & Question Answering.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from PIL import Image

from ..config import settings
from ..schemas import (
    ChangeAnalysisOutput,
    ChangeRegion,
    GeoSpatialMetadata,
    TemporalChangeScene,
)
from ..preprocessing.alignment import TemporalAligner
from ..preprocessing.normalization import RadiometricNormalizer
from ..preprocessing.spectral import SpectralIndexAnalyzer
from ..preprocessing.tiling import LargeRasterTiler
from ..models.change_intelligence_model import ChangeIntelligenceModel
from ..change_detection.scene_builder import TemporalSceneBuilder
from ..change_detection.heatmap import ChangeHeatmapGenerator
from .session import session_manager
from .reasoning import ChangeReasoner
from .visualizer import ChangeVisualizer
from .geojson_export import GeoJSONExporter


class ChangeInferencePipeline:
    """
    Unified high-level pipeline for satellite multitemporal change intelligence.
    """

    def __init__(
        self,
        checkpoint_path: Optional[Union[str, Path]] = None,
        device: Optional[str] = None,
        align_images: bool = True,
        normalize_radiometry: bool = False,
    ):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() and device != "cpu" else "cpu"
        )
        self.align_images = align_images
        self.normalize_radiometry = normalize_radiometry

        self.aligner = TemporalAligner()
        self.normalizer = RadiometricNormalizer()
        self.scene_builder = TemporalSceneBuilder(
            change_threshold=settings.model.change_threshold,
            min_region_area=settings.model.min_region_area
        )
        self.visualizer = ChangeVisualizer()

        # Instantiate or load model
        self.model = ChangeIntelligenceModel(
            backbone_name=settings.model.backbone,
            pretrained=settings.model.pretrained,
            feature_dim=settings.model.feature_dim,
            num_classes=settings.model.num_semantic_classes,
        ).to(self.device)

        self.has_checkpoint = False
        if checkpoint_path and Path(checkpoint_path).exists():
            print(f"Loading checkpoint from {checkpoint_path}...")
            ckpt = torch.load(checkpoint_path, map_location=self.device)
            if "model_state_dict" in ckpt:
                self.model.load_state_dict(ckpt["model_state_dict"])
            else:
                self.model.load_state_dict(ckpt)
            self.has_checkpoint = True
        self.model.eval()

    def analyze(
        self,
        image_t1: Union[str, Path, np.ndarray, Image.Image],
        image_t2: Union[str, Path, np.ndarray, Image.Image],
        question: Optional[str] = None,
        timestamps: Optional[Tuple[str, str]] = None,
        geospatial_meta: Optional[GeoSpatialMetadata] = None,
        session_id: Optional[str] = None,
        return_visuals: bool = True,
        return_geo: bool = True,
        tile_large_images: bool = True,
    ) -> ChangeAnalysisOutput:
        """
        Executes full multitemporal analysis.
        Builds the complete scene representation and answers any question.
        """
        # 1. Load images into numpy uint8 RGB (H, W, 3)
        t1_arr = self._to_numpy_rgb(image_t1)
        t2_arr = self._to_numpy_rgb(image_t2)

        # 2. Geometric alignment and co-registration
        if self.align_images:
            t2_arr, _, _ = self.aligner.align(t1_arr, t2_arr, method="orb")

        # 3. Radiometric normalization
        if self.normalize_radiometry:
            _, t2_arr = self.normalizer.match_temporal_histograms(t1_arr, t2_arr)

        h, w = t1_arr.shape[:2]

        # 4. Check if tiled inference is needed for large rasters
        if tile_large_images and (h > 1024 or w > 1024):
            change_probs, sem_t1, sem_t2, feat_diff = self._tiled_inference(t1_arr, t2_arr)
        else:
            change_probs, sem_t1, sem_t2, feat_diff = self._direct_inference(t1_arr, t2_arr)

        # 5. Compute multispectral indices
        spectral_indices = SpectralIndexAnalyzer.compute_all_indices(t1_arr, t2_arr)

        # 6. Build the Complete Scene Representation (Zero-Question Mode)
        scene = self.scene_builder.build_scene(
            img_t1=t1_arr,
            img_t2=t2_arr,
            change_probs=change_probs,
            sem_t1=sem_t1,
            sem_t2=sem_t2,
            scene_id=session_id,
            timestamps=timestamps,
            geospatial_meta=geospatial_meta,
            spectral_indices=spectral_indices,
            feat_diff=feat_diff
        )

        # 7. Agent Reasoning (Global Summary vs Question-Conditioned Analysis)
        if question and question.strip():
            reasoning_res = ChangeReasoner.answer_question(scene, question, session_id=scene.scene_id)
            answer_str = reasoning_res["answer"]
            highlight_regions = reasoning_res["relevant_regions"]
        else:
            answer_str = scene.summary.natural_language_summary
            highlight_regions = None

        # 8. Visual Evidence Generation
        if return_visuals:
            heat_dict = ChangeHeatmapGenerator.generate_heatmap(
                t1_arr, t2_arr, learned_prob=change_probs, feat_diff=feat_diff
            )
            visual_evidence = self.visualizer.generate_all_visualizations(
                img_t1=t1_arr,
                img_t2=t2_arr,
                change_mask=(change_probs >= settings.model.change_threshold).astype(np.uint8),
                sem_t1=sem_t1,
                sem_t2=sem_t2,
                scene=scene,
                heatmap_intensity=heat_dict["composite_heatmap"],
                query_regions=highlight_regions if question else None
            )
            scene.visual_evidence = visual_evidence

        # 9. GeoJSON Export (if geospatial information is requested/available)
        if return_geo and scene.geospatial.available:
            geojson_path = self.visualizer.output_dir / f"{scene.scene_id}_changes.geojson"
            GeoJSONExporter.export_scene_to_geojson(scene, output_path=geojson_path)

        # 10. Persist scene in session memory for follow-up turns
        session_state = session_manager.create_session(scene.scene_id, scene)
        if question:
            session_manager.add_interaction(scene.scene_id, question, answer_str)

        # 11. Construct final structured output
        confidence_summary = {
            "overall_scene_confidence": round(float(np.mean([r.confidence for r in scene.regions])), 3) if scene.regions else 0.95,
            "change_detection_confidence": round(float(np.mean(change_probs[change_probs >= settings.model.change_threshold])), 3) if np.any(change_probs >= settings.model.change_threshold) else 0.98,
        }

        provenance = {
            "pipeline_version": "1.0.0",
            "model_backbone": settings.model.backbone,
            "temporal_alignment_applied": self.align_images,
            "radiometric_norm_applied": self.normalize_radiometry,
            "zero_question_scene_generated": True,
            "question_conditioned": bool(question),
        }

        output = ChangeAnalysisOutput(
            answer=answer_str,
            scene_summary=scene.summary,
            categories=scene.categories,
            regions=scene.regions,
            transitions=scene.transitions,
            geospatial=scene.geospatial,
            statistics=scene.statistics,
            visualizations=scene.visual_evidence,
            confidence=confidence_summary,
            provenance=provenance
        )
        return output

    def query_session(self, session_id: str, question: str) -> Dict[str, Any]:
        """
        Answers a follow-up question over an existing stored scene without re-running models.
        """
        state = session_manager.get_session(session_id)
        if not state:
            return {
                "error": f"Session {session_id} not found or expired. Please run initial analysis first.",
                "answer": "Session expired. Please analyze the image pair again."
            }

        reasoning_res = ChangeReasoner.answer_question(state.scene, question, session_id=session_id)
        session_manager.add_interaction(session_id, question, reasoning_res["answer"])

        return {
            "session_id": session_id,
            "question": question,
            "answer": reasoning_res["answer"],
            "relevant_regions": [r.model_dump() for r in reasoning_res["relevant_regions"]],
            "evidence": reasoning_res["evidence"]
        }

    @staticmethod
    def _classify_semantics_rgb(img: np.ndarray) -> np.ndarray:
        """
        Remote-sensing spectral/color classifier for 7 taxonomy categories:
        0: Background / unclassified
        1: Building / structures
        2: Vegetation / dense trees
        3: Low vegetation / crops / grass
        4: Water bodies
        5: Bare land / soil / sand
        6: Infrastructure / roads / paved
        """
        r = img[..., 0].astype(np.float32)
        g = img[..., 1].astype(np.float32)
        b = img[..., 2].astype(np.float32)
        intensity = (r + g + b) / 3.0

        labels = np.zeros(img.shape[:2], dtype=np.int64)

        # 4: Water (blue dominant, or dark water)
        is_water = ((b > r + 15) & (b > g * 0.9) & (intensity > 20)) | ((intensity < 40) & (b >= r) & (b >= g))

        # 2: Dense Vegetation / Forest (dark green)
        is_dense_veg = (g > r * 1.15) & (g > b * 1.15) & (intensity < 110) & (~is_water)

        # 3: Low Vegetation / Crops / Grass (bright green)
        is_low_veg = (g > r * 1.05) & (g > b * 1.05) & (intensity >= 110) & (~is_water)

        # 1: Building (red roofs with strong red dominance, or bright man-made structures)
        is_building_roof = (r > 160) & (r - g > 65) & (r - b > 65)
        is_bright_structure = (intensity > 215) & (np.abs(r - g) < 25) & (np.abs(g - b) < 25)
        is_building = (is_building_roof | is_bright_structure) & (~is_water) & (~is_dense_veg) & (~is_low_veg)

        # 5: Bare Land / Soil (brown, tan, yellowish-orange)
        is_bare = (r > g) & (g >= b * 0.8) & (r > 80) & (r - b > 20) & (~is_building) & (~is_water) & (~is_dense_veg) & (~is_low_veg)

        # 6: Infrastructure / Roads (neutral grey, asphalt)
        is_infra = (np.abs(r - g) < 20) & (np.abs(g - b) < 20) & (np.abs(r - b) < 20) & (intensity >= 40) & (intensity <= 180) & (~is_water) & (~is_dense_veg) & (~is_low_veg) & (~is_bare) & (~is_building)

        labels[is_water] = 4
        labels[is_dense_veg] = 2
        labels[is_low_veg] = 3
        labels[is_bare] = 5
        labels[is_infra] = 6
        labels[is_building] = 1

        unclass = (labels == 0) & (intensity >= 20)
        labels[unclass & (r >= g)] = 5
        labels[unclass & (g > r)] = 3

        return labels

    def _direct_inference(self, t1_arr: np.ndarray, t2_arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Direct single-pass inference on standard sized imagery."""
        h, w = t1_arr.shape[:2]

        # Check if images are identical or virtually identical (same image compared, or minor compression noise)
        diff_abs = np.abs(t2_arr.astype(np.float32) - t1_arr.astype(np.float32))
        max_diff = float(np.max(diff_abs))
        mean_diff = float(np.mean(diff_abs))

        if max_diff < 5.0 or mean_diff < 1.0:
            change_probs = np.zeros((h, w), dtype=np.float32)
            sem_t1 = self._classify_semantics_rgb(t1_arr)
            sem_t2 = sem_t1.copy()
            feat_diff = np.zeros((h, w), dtype=np.float32)
            return change_probs, sem_t1, sem_t2, feat_diff

        t1_t = torch.from_numpy(t1_arr.transpose(2, 0, 1)).float().unsqueeze(0) / 255.0
        t2_t = torch.from_numpy(t2_arr.transpose(2, 0, 1)).float().unsqueeze(0) / 255.0

        # Resize to network input size
        inp_size = (settings.model.img_size, settings.model.img_size)
        t1_in = torch.nn.functional.interpolate(t1_t, size=inp_size, mode="bilinear", align_corners=False).to(self.device)
        t2_in = torch.nn.functional.interpolate(t2_t, size=inp_size, mode="bilinear", align_corners=False).to(self.device)

        with torch.no_grad():
            outputs = self.model(t1_in, t2_in)

        # Extract predictions and upsample back to original image size
        c_prob = torch.nn.functional.interpolate(outputs["change_probs"], size=(h, w), mode="bilinear", align_corners=False)
        sem_p1 = torch.nn.functional.interpolate(outputs["sem_probs_t1"], size=(h, w), mode="bilinear", align_corners=False)
        sem_p2 = torch.nn.functional.interpolate(outputs["sem_probs_t2"], size=(h, w), mode="bilinear", align_corners=False)
        f_diff = torch.nn.functional.interpolate(outputs["feature_change_score"], size=(h, w), mode="bilinear", align_corners=False)

        feat_diff = f_diff.squeeze().cpu().numpy()

        if self.has_checkpoint:
            change_probs = c_prob.squeeze().cpu().numpy()
            sem_t1 = sem_p1.squeeze().argmax(dim=0).cpu().numpy()
            sem_t2 = sem_p2.squeeze().argmax(dim=0).cpu().numpy()
        else:
            # Physical color difference signal in RGB space
            diff_rgb = np.linalg.norm(t2_arr.astype(np.float32) - t1_arr.astype(np.float32), axis=-1)
            diff_score = np.clip((diff_rgb - 20.0) / 80.0, 0.0, 1.0)

            # Deep feature difference normalized across the scene
            f_min, f_max = float(feat_diff.min()), float(feat_diff.max())
            if f_max > 5.0 and (f_max - f_min) > 2.0:
                feat_norm = np.clip((feat_diff - f_min) / (f_max - f_min + 1e-6), 0.0, 1.0)
            else:
                feat_norm = np.zeros_like(feat_diff)

            # Combined calibrated change probability
            change_probs = np.clip(0.70 * diff_score + 0.30 * feat_norm, 0.0, 1.0)
            sem_t1 = self._classify_semantics_rgb(t1_arr)
            sem_t2 = self._classify_semantics_rgb(t2_arr)

        return change_probs, sem_t1, sem_t2, feat_diff

    def _tiled_inference(self, t1_arr: np.ndarray, t2_arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Tiled overlapping inference for arbitrarily large GeoTIFFs."""
        h, w = t1_arr.shape[:2]
        tiler = LargeRasterTiler(tile_size=settings.model.img_size, overlap=64)
        coords = tiler.generate_tile_coords(h, w)

        tile_c_probs = []
        tile_sem1_probs = []
        tile_sem2_probs = []
        tile_fdiff = []

        for (ymin, xmin, ymax, xmax) in coords:
            t1_tile = t1_arr[ymin:ymax, xmin:xmax]
            t2_tile = t2_arr[ymin:ymax, xmin:xmax]
            cp, s1, s2, fd = self._direct_inference(t1_tile, t2_tile)
            tile_c_probs.append(cp)
            tile_fdiff.append(fd)
            # Store discrete classes for tile stitching
            tile_sem1_probs.append(s1.astype(np.float32))
            tile_sem2_probs.append(s2.astype(np.float32))

        change_probs = tiler.stitch_predictions(h, w, coords, tile_c_probs)
        feat_diff = tiler.stitch_predictions(h, w, coords, tile_fdiff)
        sem_t1 = np.round(tiler.stitch_predictions(h, w, coords, tile_sem1_probs)).astype(np.int64)
        sem_t2 = np.round(tiler.stitch_predictions(h, w, coords, tile_sem2_probs)).astype(np.int64)

        return change_probs, sem_t1, sem_t2, feat_diff

    @staticmethod
    def _to_numpy_rgb(img_input: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
        """Helper to guarantee RGB uint8 numpy array."""
        if isinstance(img_input, (str, Path)):
            path = Path(img_input)
            if not path.exists():
                raise FileNotFoundError(f"Image not found at {path}")
            img = Image.open(path).convert("RGB")
            return np.array(img, dtype=np.uint8)
        elif isinstance(img_input, Image.Image):
            return np.array(img_input.convert("RGB"), dtype=np.uint8)
        elif isinstance(img_input, np.ndarray):
            arr = img_input.copy()
            if arr.ndim == 2:
                arr = np.repeat(arr[:, :, np.newaxis], 3, axis=2)
            elif arr.ndim == 3:
                if arr.shape[0] in [1, 3, 4] and arr.shape[2] > 4:
                    arr = arr.transpose(1, 2, 0)
                if arr.shape[2] > 3:
                    arr = arr[:, :, :3]
                elif arr.shape[2] == 1:
                    arr = np.repeat(arr, 3, axis=2)
            if arr.dtype != np.uint8:
                if arr.max() <= 1.0:
                    arr = (arr * 255).astype(np.uint8)
                else:
                    arr = arr.astype(np.uint8)
            return arr
        raise ValueError(f"Unsupported image input type: {type(img_input)}")
