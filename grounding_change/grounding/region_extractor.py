"""
Connected Component Region Extractor & Spatial Analyzer.
Extracts individual changed spatial objects/regions from dense segmentation masks.
Computes bounding boxes, centroids, pixel areas, and run-length-encoded (RLE) masks.
Never treats an entire scene as a single bounding box.
"""

from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np
from ..schemas import BoundingBox, ChangeRegion
from ..taxonomy import ChangeType, taxonomy


def encode_rle(binary_mask: np.ndarray) -> str:
    """Run-length encode a 2D boolean or uint8 mask into a compact string."""
    pixels = binary_mask.flatten()
    runs = []
    prev = -1
    count = 0
    for p in pixels:
        val = 1 if p > 0 else 0
        if val == prev:
            count += 1
        else:
            if prev != -1:
                runs.append(f"{prev}:{count}")
            prev = val
            count = 1
    if prev != -1:
        runs.append(f"{prev}:{count}")
    return ",".join(runs)


def decode_rle(rle_str: str, shape: Tuple[int, int]) -> np.ndarray:
    """Decode an RLE string back to a 2D uint8 mask."""
    pixels = []
    for part in rle_str.split(","):
        if not part:
            continue
        val_str, count_str = part.split(":")
        pixels.extend([int(val_str)] * int(count_str))
    return np.array(pixels, dtype=np.uint8).reshape(shape)


class RegionExtractor:
    """
    Extracts individual localized regions from binary change and semantic maps.
    """

    def __init__(self, min_area_pixels: int = 16, connectivity: int = 8):
        self.min_area_pixels = min_area_pixels
        self.connectivity = connectivity

    def extract_regions(
        self,
        change_mask: np.ndarray,
        sem_t1: Optional[np.ndarray] = None,
        sem_t2: Optional[np.ndarray] = None,
        confidence_map: Optional[np.ndarray] = None
    ) -> List[ChangeRegion]:
        """
        Segment change mask into discrete regions and assign category + change type.

        change_mask: (H, W) uint8 or bool (1=change, 0=no change)
        sem_t1: (H, W) category IDs for T1
        sem_t2: (H, W) category IDs for T2
        confidence_map: (H, W) float in [0, 1]
        """
        binary = (change_mask > 0).astype(np.uint8)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary, connectivity=self.connectivity
        )

        regions: List[ChangeRegion] = []
        region_counter = 1

        for label_id in range(1, num_labels):  # 0 is background
            area = int(stats[label_id, cv2.CC_STAT_AREA])
            if area < self.min_area_pixels:
                continue

            x_min = int(stats[label_id, cv2.CC_STAT_LEFT])
            y_min = int(stats[label_id, cv2.CC_STAT_TOP])
            w = int(stats[label_id, cv2.CC_STAT_WIDTH])
            h = int(stats[label_id, cv2.CC_STAT_HEIGHT])
            x_max = x_min + w
            y_max = y_min + h

            c_col = int(round(centroids[label_id][0]))
            c_row = int(round(centroids[label_id][1]))

            # Create individual region mask
            region_mask = (labels == label_id).astype(np.uint8)
            rle_mask = encode_rle(region_mask)

            # Determine dominant category in T1 and T2 for this region
            t1_name = "unknown"
            t2_name = "unknown"
            cat_name = "building"  # Default fallback
            ch_type = ChangeType.ADDED.value

            if sem_t1 is not None and sem_t2 is not None:
                t1_pixels = sem_t1[region_mask > 0]
                t2_pixels = sem_t2[region_mask > 0]

                if len(t1_pixels) > 0 and len(t2_pixels) > 0:
                    t1_dom_id = int(np.bincount(t1_pixels).argmax())
                    t2_dom_id = int(np.bincount(t2_pixels).argmax())
                    t1_name = taxonomy.get_by_id(t1_dom_id).name
                    t2_name = taxonomy.get_by_id(t2_dom_id).name

                    # Determine primary category and change type
                    if t1_name in ["background", "bare_land"] and t2_name not in ["background", "bare_land"]:
                        cat_name = t2_name
                        ch_type = ChangeType.ADDED.value
                    elif t1_name not in ["background", "bare_land"] and t2_name in ["background", "bare_land"]:
                        cat_name = t1_name
                        ch_type = ChangeType.REMOVED.value
                    elif t1_name == t2_name and t1_name not in ["background", "bare_land"]:
                        cat_name = t2_name
                        ch_type = ChangeType.EXPANDED.value
                    else:
                        cat_name = t2_name if t2_name != "background" else t1_name
                        ch_type = ChangeType.CONVERTED.value

            # Region average confidence
            if confidence_map is not None:
                conf = float(np.mean(confidence_map[region_mask > 0]))
            else:
                conf = 0.92

            region = ChangeRegion(
                region_id=f"R{region_counter:02d}",
                category=cat_name,
                change_type=ch_type,
                confidence=round(conf, 4),
                bbox=[x_min, y_min, x_max, y_max],
                mask_rle=rle_mask,
                centroid_pixel=[c_col, c_row],
                area_pixels=area,
                t1_dominant_class=t1_name,
                t2_dominant_class=t2_name
            )
            regions.append(region)
            region_counter += 1

        # Sort regions descending by area
        regions.sort(key=lambda r: r.area_pixels, reverse=True)
        return regions
