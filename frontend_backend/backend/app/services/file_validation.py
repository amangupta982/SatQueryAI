import os
from fastapi import UploadFile
from app.core.config import core_settings
from app.core.exceptions import InvalidImageError, FileTooLargeError, PathTraversalError

class FileValidationService:
    @staticmethod
    def validate_filename(filename: str) -> None:
        """Ensure the filename doesn't attempt path traversal."""
        if not filename:
            raise InvalidImageError("Filename is missing.")
            
        # Prevent path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise PathTraversalError(f"Malicious filename detected: {filename}")

    @staticmethod
    def validate_extension(filename: str) -> None:
        """Ensure the file extension is allowed."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in core_settings.ALLOWED_EXTENSIONS:
            raise InvalidImageError(f"Extension '{ext}' is not allowed. Allowed: {core_settings.ALLOWED_EXTENSIONS}")

    @staticmethod
    async def validate_file_size(file: UploadFile) -> None:
        """
        Validate file size by seeking to the end of the file.
        This is safer than relying on Content-Length header.
        """
        # Await file reading to get to end, or use spool check
        file.file.seek(0, 2)  # seek to end
        size = file.file.tell()
        file.file.seek(0)     # reset pointer

        if size > core_settings.MAX_UPLOAD_SIZE:
            mb_size = core_settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise FileTooLargeError(f"File exceeds maximum allowed size of {mb_size} MB.")

    @classmethod
    async def validate_upload(cls, file: UploadFile) -> None:
        """Run all validations on an uploaded file."""
        cls.validate_filename(file.filename)
        cls.validate_extension(file.filename)
        await cls.validate_file_size(file)
