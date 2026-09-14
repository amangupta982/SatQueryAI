"""
Image preprocessing for the Area Measurement module.

Handles loading of standard RGB images, GeoTIFF (with spatial metadata),
and multi-band satellite imagery. Automatically detects image format and
extracts spatial resolution when available.
"""

import numpy as np
from PIL import Image
import os

# Optional: rasterio for GeoTIFF support
try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False


class ImageData:
    """
    Container for loaded image data and metadata.
    
    Attributes:
        image_rgb: np.ndarray of shape (H, W, 3) in RGB uint8.
        original_size: (width, height) of the original image.
        spatial_resolution: float or None. Meters per pixel if known.
        is_geotiff: bool. Whether the image had geospatial metadata.
        crs: Coordinate reference system string, if available.
        transform: Affine transform, if available.
        num_bands: Number of bands in the original file.
        source_path: Original file path.
    """

    def __init__(self):
        self.image_rgb = None
        self.original_size = None
        self.spatial_resolution = None
        self.is_geotiff = False
        self.crs = None
        self.transform = None
        self.num_bands = 3
        self.source_path = None


def load_image(source) -> ImageData:
    """
    Load an image from a file path, PIL Image, or numpy array.
    
    Automatically detects:
    - Standard RGB images (PNG, JPEG, BMP, etc.)
    - GeoTIFF with spatial metadata
    - Multi-band satellite imagery
    
    Args:
        source: str (file path), PIL.Image, or np.ndarray (H, W, 3).
        
    Returns:
        ImageData object with normalized RGB image and metadata.
        
    Raises:
        ValueError: If the source cannot be loaded.
        FileNotFoundError: If the file path doesn't exist.
    """
    data = ImageData()

    if isinstance(source, np.ndarray):
        return _load_from_array(source, data)
    elif isinstance(source, Image.Image):
        return _load_from_pil(source, data)
    elif isinstance(source, str):
        return _load_from_path(source, data)
    else:
        raise ValueError(
            f"Unsupported source type: {type(source)}. "
            "Expected file path (str), PIL.Image, or numpy array."
        )


def _load_from_array(arr: np.ndarray, data: ImageData) -> ImageData:
    """Load from a numpy array."""
    if arr.ndim == 2:
        # Grayscale → RGB
        arr = np.stack([arr, arr, arr], axis=-1)
    elif arr.ndim == 3 and arr.shape[2] == 4:
        # RGBA → RGB
        arr = arr[:, :, :3]
    elif arr.ndim == 3 and arr.shape[2] > 4:
        # Multi-band → use first 3 bands as RGB proxy
        arr = _select_rgb_bands(arr)

    if arr.dtype != np.uint8:
        arr = _normalize_to_uint8(arr)

    data.image_rgb = arr
    data.original_size = (arr.shape[1], arr.shape[0])
    data.num_bands = arr.shape[2] if arr.ndim == 3 else 1
    return data


def _load_from_pil(img: Image.Image, data: ImageData) -> ImageData:
    """Load from a PIL Image."""
    img_rgb = img.convert("RGB")
    arr = np.array(img_rgb)
    data.image_rgb = arr
    data.original_size = img.size  # (width, height)
    data.source_path = getattr(img, "filename", None)
    return data


def _load_from_path(path: str, data: ImageData) -> ImageData:
    """Load from a file path, using rasterio for GeoTIFF if available."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")

    data.source_path = path
    ext = os.path.splitext(path)[1].lower()

    # Try GeoTIFF with rasterio first
    if ext in (".tif", ".tiff") and HAS_RASTERIO:
        return _load_geotiff(path, data)

    # Standard image formats
    try:
        img = Image.open(path)
        return _load_from_pil(img, data)
    except Exception as e:
        raise ValueError(f"Cannot load image from {path}: {e}")


def _load_geotiff(path: str, data: ImageData) -> ImageData:
    """
    Load a GeoTIFF file with spatial metadata extraction.
    
    Extracts:
    - RGB composite from available bands
    - Spatial resolution from transform
    - CRS information
    """
    with rasterio.open(path) as src:
        data.is_geotiff = True
        data.crs = str(src.crs) if src.crs else None
        data.transform = src.transform
        data.num_bands = src.count
        data.original_size = (src.width, src.height)

        # Extract spatial resolution (meters per pixel)
        if src.transform and src.crs:
            # Resolution is the pixel size in the CRS units
            res_x = abs(src.transform[0])
            res_y = abs(src.transform[4])
            data.spatial_resolution = (res_x + res_y) / 2.0

        # Read bands
        bands = src.read()  # shape: (num_bands, H, W)

        if src.count >= 3:
            # Use bands 1, 2, 3 as RGB (or bands 4, 3, 2 for Sentinel-2 natural color)
            if src.count >= 4:
                # Sentinel-2: B4=Red, B3=Green, B2=Blue (bands are 1-indexed)
                rgb = np.stack([bands[2], bands[1], bands[0]], axis=-1)
            else:
                rgb = np.stack([bands[0], bands[1], bands[2]], axis=-1)
        elif src.count == 1:
            # Single band → grayscale
            rgb = np.stack([bands[0], bands[0], bands[0]], axis=-1)
        else:
            rgb = np.stack([bands[0], bands[1 % src.count], bands[2 % src.count]], axis=-1)

        data.image_rgb = _normalize_to_uint8(rgb)

    return data


def _select_rgb_bands(multi_band: np.ndarray) -> np.ndarray:
    """
    Select RGB bands from a multi-band image.
    For Sentinel-2: use bands at indices 3 (B4/Red), 2 (B3/Green), 1 (B2/Blue).
    Fallback: first 3 bands.
    """
    if multi_band.shape[2] >= 4:
        # Assume Sentinel-2 band ordering: B2, B3, B4, B8, ...
        return multi_band[:, :, [2, 1, 0]]  # R, G, B
    return multi_band[:, :, :3]


def _normalize_to_uint8(arr: np.ndarray) -> np.ndarray:
    """
    Normalize array values to uint8 range [0, 255].
    Handles various data types (float, int16, uint16, etc.)
    """
    if arr.dtype == np.uint8:
        return arr

    # For float types
    if np.issubdtype(arr.dtype, np.floating):
        if arr.max() <= 1.0:
            return (arr * 255).clip(0, 255).astype(np.uint8)
        else:
            # Percentile stretch for satellite imagery
            p2, p98 = np.percentile(arr[arr > 0], [2, 98]) if arr.any() else (0, 1)
            if p98 == p2:
                p98 = p2 + 1
            stretched = (arr - p2) / (p98 - p2) * 255
            return stretched.clip(0, 255).astype(np.uint8)

    # For integer types (e.g., uint16 from satellite sensors)
    if arr.max() > 255:
        p2, p98 = np.percentile(arr[arr > 0], [2, 98]) if arr.any() else (0, 1)
        if p98 == p2:
            p98 = p2 + 1
        stretched = (arr.astype(np.float32) - p2) / (p98 - p2) * 255
        return stretched.clip(0, 255).astype(np.uint8)

    return arr.astype(np.uint8)


def prepare_for_model(image_rgb: np.ndarray, target_size: tuple = (520, 520)) -> np.ndarray:
    """
    Prepare image for model input: resize and normalize.
    
    Args:
        image_rgb: (H, W, 3) uint8 array.
        target_size: (width, height) for model input.
        
    Returns:
        (H, W, 3) uint8 resized image.
    """
    img = Image.fromarray(image_rgb)
    img_resized = img.resize(target_size, Image.BILINEAR)
    return np.array(img_resized)
