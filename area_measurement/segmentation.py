"""
Semantic segmentation engine for the Area Measurement module.

Provides two segmentation strategies:
1. DeepLabV3-ResNet101 (torchvision) — for general images
2. HSV color-space analysis — optimized fallback for satellite imagery

The segmentation produces pixel-level class masks aligned with the
BigEarthNet CLC-derived land-cover taxonomy.
"""

import numpy as np
from PIL import Image
import cv2
import torch
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet101, DeepLabV3_ResNet101_Weights
from scipy import ndimage

from area_measurement.config import (
    LAND_COVER_CLASSES,
    VOC_TO_LANDCOVER,
    MIN_REGION_AREA_PX,
    MODEL_INPUT_SIZE,
    SEGMENTATION_CONFIDENCE_THRESHOLD,
)


class SemanticSegmenter:
    """
    Land-cover semantic segmentation engine.
    
    Uses DeepLabV3-ResNet101 pretrained on COCO/VOC as the primary model,
    with a satellite-optimized HSV color-space fallback for remote sensing images.
    
    The model produces a class mask aligned to our land-cover taxonomy
    (derived from BigEarthNet CLC-19 nomenclature).
    """

    def __init__(self, device: str = None):
        """
        Initialize the segmenter.
        
        Args:
            device: 'cuda', 'cpu', or None for auto-detection.
        """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model = None
        self.transform = None
        self._model_loaded = False

    def _load_model(self):
        """Lazy-load the DeepLabV3 model (downloads weights on first use ~233MB)."""
        if self._model_loaded:
            return

        print("[Area Measurement] Loading DeepLabV3-ResNet101 model...")
        weights = DeepLabV3_ResNet101_Weights.DEFAULT
        self.model = deeplabv3_resnet101(weights=weights)
        self.model.to(self.device)
        self.model.eval()

        self.transform = T.Compose([
            T.ToTensor(),
            T.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

        self._model_loaded = True
        print("[Area Measurement] Model loaded successfully.")

    def segment(self, image_rgb: np.ndarray, use_satellite_mode: bool = False) -> np.ndarray:
        """
        Perform semantic segmentation on an image.
        
        Args:
            image_rgb: (H, W, 3) uint8 RGB image.
            use_satellite_mode: If True, use HSV-based segmentation optimized
                                for satellite imagery.
        
        Returns:
            class_mask: (H, W) int array of land-cover class IDs.
        """
        if use_satellite_mode:
            raw_mask = self._segment_satellite(image_rgb)
        else:
            raw_mask = self._segment_deeplab(image_rgb)

        # Apply minimum area filtering
        filtered_mask = self._filter_small_regions(raw_mask)

        return filtered_mask

    def _segment_deeplab(self, image_rgb: np.ndarray) -> np.ndarray:
        """
        Segment using DeepLabV3-ResNet101.
        
        Returns class mask at original image resolution.
        """
        self._load_model()

        h, w = image_rgb.shape[:2]

        # Prepare input
        img_pil = Image.fromarray(image_rgb)
        input_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)

        # Inference
        with torch.no_grad():
            output = self.model(input_tensor)["out"]

        # Get class predictions
        voc_mask = output.argmax(dim=1).squeeze().cpu().numpy()

        # Resize to original resolution
        voc_mask_resized = cv2.resize(
            voc_mask.astype(np.uint8),
            (w, h),
            interpolation=cv2.INTER_NEAREST,
        )

        # Map VOC classes to our land-cover taxonomy
        landcover_mask = np.vectorize(
            lambda x: VOC_TO_LANDCOVER.get(x, 0)
        )(voc_mask_resized)

        # For satellite-like images, if DeepLabV3 mostly predicts background,
        # fall back to HSV analysis
        non_bg_ratio = np.sum(landcover_mask > 0) / landcover_mask.size
        if non_bg_ratio < 0.05:
            # DeepLabV3 couldn't detect much — use satellite mode
            print("[Area Measurement] Low detection rate, switching to satellite analysis mode.")
            return self._segment_satellite(image_rgb)

        return landcover_mask.astype(np.int32)

    def _segment_satellite(self, image_rgb: np.ndarray) -> np.ndarray:
        """
        Satellite-optimized segmentation using HSV color-space analysis.
        
        Uses spectral characteristics typical of satellite imagery:
        - Vegetation: high green values, specific HSV ranges
        - Water: dark blue areas
        - Urban/Building: grey, high brightness, low saturation
        - Bare land: brown/tan colors
        - Agriculture: bright green-yellow
        - Forest: dark green
        - Roads: grey linear features
        """
        h, w = image_rgb.shape[:2]
        hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
        mask = np.zeros((h, w), dtype=np.int32)

        hue = hsv[:, :, 0]
        sat = hsv[:, :, 1]
        val = hsv[:, :, 2]

        # ── Water Detection ──
        # Water appears dark blue/blue-green in satellite imagery
        water = (
            ((hue >= 90) & (hue <= 130) & (sat >= 30) & (val >= 20)) |  # Blue water
            ((hue >= 85) & (hue <= 135) & (sat >= 20) & (val <= 80))     # Dark water
        )
        mask[water] = 6  # Water

        # ── Forest Detection ──
        # Dense forest: dark green with high saturation
        forest = (
            (hue >= 35) & (hue <= 80) &
            (sat >= 60) & (val >= 30) & (val <= 150) &
            (~water)
        )
        mask[forest] = 4  # Forest

        # ── Vegetation Detection ──
        # Lighter green areas (grassland, scrub, etc.)
        vegetation = (
            (hue >= 25) & (hue <= 90) &
            (sat >= 30) & (sat < 60) &
            (val >= 50) &
            (~water) & (~forest)
        )
        mask[vegetation] = 5  # Vegetation

        # ── Agriculture Detection ──
        # Bright green-yellow cultivated areas
        agriculture = (
            (hue >= 20) & (hue <= 45) &
            (sat >= 40) & (val >= 100) &
            (~water) & (~forest) & (~vegetation)
        )
        mask[agriculture] = 3  # Agriculture

        # ── Bare Land Detection ──
        # Brown/tan/sandy areas
        bare_land = (
            (hue >= 8) & (hue <= 25) &
            (sat >= 30) & (sat <= 180) &
            (val >= 80) &
            (~water) & (~forest) & (~vegetation) & (~agriculture)
        )
        mask[bare_land] = 8  # Bare Land

        # ── Building / Urban Detection ──
        # Grey areas with low saturation and medium-high brightness
        urban = (
            (sat <= 40) &
            (val >= 100) & (val <= 220) &
            (~water) & (~forest) & (~vegetation) & (~agriculture) & (~bare_land)
        )
        mask[urban] = 1  # Building / Urban

        # ── Road Detection ──
        # Very grey, narrow features (hard to detect without shape analysis)
        road = (
            (sat <= 25) &
            (val >= 80) & (val <= 180) &
            (mask == 0) &
            (~water)
        )
        mask[road] = 9  # Road

        # ── Wetland Detection ──
        # Mix of water and vegetation characteristics
        wetland = (
            (hue >= 60) & (hue <= 100) &
            (sat >= 20) & (sat <= 80) &
            (val >= 30) & (val <= 120) &
            (mask == 0)
        )
        mask[wetland] = 7  # Wetland

        # ── Industrial Detection ──
        # Very bright grey/white areas
        industrial = (
            (sat <= 30) &
            (val >= 220) &
            (mask == 0)
        )
        mask[industrial] = 2  # Industrial

        return mask

    def _filter_small_regions(self, mask: np.ndarray) -> np.ndarray:
        """
        Remove small noisy regions below the minimum area threshold.
        Uses connected component analysis per class.
        """
        filtered = mask.copy()
        unique_classes = np.unique(mask)

        for cls_id in unique_classes:
            if cls_id == 0:  # Skip background
                continue

            class_binary = (mask == cls_id).astype(np.uint8)
            labeled, num_features = ndimage.label(class_binary)
            
            if num_features == 0:
                continue

            # Fast vectorized region size calculation
            region_sizes = np.bincount(labeled.ravel())
            
            # Identify which regions are smaller than the threshold
            too_small = region_sizes < MIN_REGION_AREA_PX
            too_small[0] = False  # Ignore background of this mask
            
            # Create a boolean mask of all pixels belonging to small regions
            small_pixels = too_small[labeled]
            
            # Set those pixels to background (0)
            filtered[small_pixels] = 0

        return filtered

    def get_connected_components(self, mask: np.ndarray, class_id: int) -> list:
        """
        Get connected components (instances) for a specific class.
        
        Args:
            mask: (H, W) class mask.
            class_id: Target class ID.
            
        Returns:
            List of binary masks, one per connected component.
        """
        class_binary = (mask == class_id).astype(np.uint8)
        labeled, num_features = ndimage.label(class_binary)

        components = []
        for region_id in range(1, num_features + 1):
            region_mask = labeled == region_id
            if np.sum(region_mask) >= MIN_REGION_AREA_PX:
                components.append(region_mask)

        return components
