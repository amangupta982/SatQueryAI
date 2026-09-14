import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class CoreSettings(BaseSettings):
    # Image Upload Settings
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: set[str] = {".tif", ".tiff", ".geotiff", ".png", ".jpg", ".jpeg"}

    # RAG Settings
    QDRANT_PATH: str = os.path.join(BASE_DIR, "data", "qdrant")
    KNOWLEDGE_DIR: str = os.path.join(BASE_DIR, "knowledge")

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

core_settings = CoreSettings()
