import pyproj
from shapely.geometry import Polygon
from app.schemas.image import ImageMetadata
from app.schemas.compatibility import CompatibilityState, CompatibilityReport

class ImageCompatibilityService:
    
    @staticmethod
    def _create_polygon_epsg4326(img: ImageMetadata) -> Polygon:
        """
        Creates a Shapely Polygon representing the image bounds in EPSG:4326.
        Bounds are assumed to be [left, bottom, right, top].
        """
        left, bottom, right, top = img.bounds
        corners = [
            (left, bottom),
            (right, bottom),
            (right, top),
            (left, top)
        ]
        
        # If CRS is already WGS84, no transformation needed
        crs_str = str(img.crs).lower()
        if crs_str in ["epsg:4326", "wgs84", "+proj=longlat +datum=wgs84 +no_defs"]:
            return Polygon(corners)
            
        transformer = pyproj.Transformer.from_crs(img.crs, "EPSG:4326", always_xy=True)
        transformed_corners = [transformer.transform(x, y) for x, y in corners]
        return Polygon(transformed_corners)

    @staticmethod
    def compare(img1: ImageMetadata, img2: ImageMetadata) -> CompatibilityReport:
        # 1. Missing Spatial Metadata
        if not all([img1.crs, img1.bounds, img1.transform, img2.crs, img2.bounds, img2.transform]):
            return CompatibilityReport(
                state=CompatibilityState.COMPATIBLE_NOT_VERIFIED,
                reasoning="Missing CRS, bounds, or transform in one or both images."
            )

        # 2. Check overlap
        try:
            poly1 = ImageCompatibilityService._create_polygon_epsg4326(img1)
            poly2 = ImageCompatibilityService._create_polygon_epsg4326(img2)
        except Exception as e:
            return CompatibilityReport(
                state=CompatibilityState.COMPATIBLE_NOT_VERIFIED,
                reasoning=f"Failed to transform bounds to standard CRS: {e}"
            )
            
        if not poly1.intersects(poly2):
            return CompatibilityReport(
                state=CompatibilityState.INCOMPATIBLE,
                reasoning="Images have zero geographic overlap."
            )
            
        intersection_area = poly1.intersection(poly2).area
        overlap_1 = (intersection_area / poly1.area) * 100 if poly1.area > 0 else 0
        overlap_2 = (intersection_area / poly2.area) * 100 if poly2.area > 0 else 0
        
        # 3. Check for exact alignment
        identical_crs = str(img1.crs).lower() == str(img2.crs).lower()
        
        # We need a small tolerance for float comparisons in transform and resolution
        def is_close_list(l1, l2, tol=1e-6):
            if len(l1) != len(l2): return False
            return all(abs(a - b) < tol for a, b in zip(l1, l2))
            
        identical_transform = is_close_list(img1.transform, img2.transform)
        identical_dimensions = (img1.width == img2.width) and (img1.height == img2.height)
        
        # Default empty list for resolution if none
        res1 = img1.resolution or []
        res2 = img2.resolution or []
        resolution_match = is_close_list(res1, res2)
        
        if identical_crs and identical_transform and identical_dimensions:
            state = CompatibilityState.ALIGNED
            reasoning = "Images are perfectly co-registered (same CRS, transform, and dimensions)."
        else:
            state = CompatibilityState.REQUIRES_REGISTRATION
            reasoning = "Images overlap spatially but have differing CRS, transforms, or dimensions."

        return CompatibilityReport(
            state=state,
            overlap_percentage_1=round(overlap_1, 2),
            overlap_percentage_2=round(overlap_2, 2),
            identical_crs=identical_crs,
            identical_transform=identical_transform,
            identical_dimensions=identical_dimensions,
            resolution_match=resolution_match,
            reasoning=reasoning
        )
