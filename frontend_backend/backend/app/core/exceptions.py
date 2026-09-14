class SatQueryError(Exception):
    """Base class for all domain-specific exceptions in SatQuery AI."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidImageError(SatQueryError):
    """Raised when an uploaded file is not a valid image format or extension."""
    def __init__(self, message: str = "Invalid image file format."):
        super().__init__(message, status_code=400)


class FileTooLargeError(SatQueryError):
    """Raised when an uploaded file exceeds the maximum allowed size."""
    def __init__(self, message: str = "File is too large."):
        super().__init__(message, status_code=413)


class RasterProcessingError(SatQueryError):
    """Raised when a raster file is corrupted or cannot be processed by Rasterio."""
    def __init__(self, message: str = "Failed to process raster file."):
        super().__init__(message, status_code=422)


class PathTraversalError(SatQueryError):
    """Raised when a file path looks malicious or attempts path traversal."""
    def __init__(self, message: str = "Invalid filename or path traversal detected."):
        super().__init__(message, status_code=400)


class ImageNotFoundError(SatQueryError):
    """Raised when an image ID cannot be found on the filesystem."""
    def __init__(self, message: str = "Image not found."):
        super().__init__(message, status_code=404)
