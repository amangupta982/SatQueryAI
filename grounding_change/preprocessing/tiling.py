"""
Large Image Tiling and Overlap Stitching.
Enables processing arbitrarily large satellite GeoTIFF scenes without GPU OOM.
Preserves geospatial coordinates and handles edge blending.
"""

from typing import Callable, Generator, List, Optional, Tuple
import numpy as np


class LargeRasterTiler:
    """
    Slices large satellite rasters into manageable overlapping tiles,
    runs inference tile-by-tile, and stitches predictions with linear blend weighting.
    """

    def __init__(self, tile_size: int = 512, overlap: int = 64):
        self.tile_size = tile_size
        self.overlap = overlap
        self.stride = tile_size - overlap
        assert self.stride > 0, "Overlap must be strictly smaller than tile_size"

    def generate_tile_coords(self, height: int, width: int) -> List[Tuple[int, int, int, int]]:
        """
        Generate (ymin, xmin, ymax, xmax) for all tiles covering (height, width).
        """
        coords = []
        y = 0
        while y < height:
            ymin = y
            ymax = min(y + self.tile_size, height)
            if ymax - ymin < self.tile_size and ymin > 0:
                ymin = max(0, height - self.tile_size)

            x = 0
            while x < width:
                xmin = x
                xmax = min(x + self.tile_size, width)
                if xmax - xmin < self.tile_size and xmin > 0:
                    xmin = max(0, width - self.tile_size)

                coords.append((ymin, xmin, ymax, xmax))
                if xmax == width:
                    break
                x += self.stride

            if ymax == height:
                break
            y += self.stride

        return coords

    def get_blend_weights(self, h: int, w: int) -> np.ndarray:
        """
        Create 2D trapezoidal/cosine blend weights tapering at borders.
        Prevents tile boundary seam artifacts during stitching.
        """
        ramp_y = np.ones(h, dtype=np.float32)
        ramp_x = np.ones(w, dtype=np.float32)

        if self.overlap > 0:
            ov = min(self.overlap // 2, h // 2, w // 2)
            if ov > 0:
                ramp_y[:ov] = np.linspace(0.1, 1.0, ov)
                ramp_y[-ov:] = np.linspace(1.0, 0.1, ov)
                ramp_x[:ov] = np.linspace(0.1, 1.0, ov)
                ramp_x[-ov:] = np.linspace(1.0, 0.1, ov)

        return np.outer(ramp_y, ramp_x)

    def stitch_predictions(
        self,
        height: int,
        width: int,
        tile_coords: List[Tuple[int, int, int, int]],
        tile_predictions: List[np.ndarray],
    ) -> np.ndarray:
        """
        Recombine tile predictions into full scene array.
        tile_predictions: list of arrays (tile_h, tile_w) or (channels, tile_h, tile_w)
        """
        sample_pred = tile_predictions[0]
        is_multi_channel = sample_pred.ndim == 3
        channels = sample_pred.shape[0] if is_multi_channel else 1

        if is_multi_channel:
            accumulator = np.zeros((channels, height, width), dtype=np.float32)
            weight_sum = np.zeros((1, height, width), dtype=np.float32)
        else:
            accumulator = np.zeros((height, width), dtype=np.float32)
            weight_sum = np.zeros((height, width), dtype=np.float32)

        for (ymin, xmin, ymax, xmax), pred in zip(tile_coords, tile_predictions):
            h_tile = ymax - ymin
            w_tile = xmax - xmin
            pred_slice = pred[..., :h_tile, :w_tile] if is_multi_channel else pred[:h_tile, :w_tile]

            weights = self.get_blend_weights(h_tile, w_tile)
            if is_multi_channel:
                accumulator[:, ymin:ymax, xmin:xmax] += pred_slice * weights[np.newaxis, ...]
                weight_sum[:, ymin:ymax, xmin:xmax] += weights[np.newaxis, ...]
            else:
                accumulator[ymin:ymax, xmin:xmax] += pred_slice * weights
                weight_sum[ymin:ymax, xmin:xmax] += weights

        weight_sum = np.maximum(weight_sum, 1e-6)
        return accumulator / weight_sum
