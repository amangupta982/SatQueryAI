import rasterio
from rasterio.errors import RasterioIOError
from app.core.exceptions import RasterProcessingError

class RasterService:
    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """
        Uses rasterio to open the image and extract relevant metadata.
        Returns a dictionary that maps to the ImageMetadata schema.
        """
        try:
            with rasterio.open(file_path) as src:
                metadata = {
                    "width": src.width,
                    "height": src.height,
                    "bands": src.count,
                    "dtype": src.dtypes[0] if src.count > 0 else "unknown",
                    "driver": src.driver,
                    "raster_metadata": src.tags()
                }

                # Try to extract geospatial metadata, but don't fail if missing (e.g. for simple PNGs)
                
                # crs
                try:
                    metadata["crs"] = src.crs.to_string() if src.crs else None
                except Exception:
                    metadata["crs"] = None
                
                # transform
                try:
                    metadata["transform"] = list(src.transform) if src.transform else None
                except Exception:
                    metadata["transform"] = None
                    
                # bounds
                try:
                    metadata["bounds"] = list(src.bounds) if src.bounds else None
                except Exception:
                    metadata["bounds"] = None
                    
                # resolution
                try:
                    metadata["resolution"] = list(src.res) if src.res else None
                except Exception:
                    metadata["resolution"] = None

                return metadata
                
        except RasterioIOError as e:
            raise RasterProcessingError(f"Could not open or process raster file: {str(e)}")
        except Exception as e:
            raise RasterProcessingError(f"Unexpected error processing raster: {str(e)}")
