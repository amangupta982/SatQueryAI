from pydantic_settings import BaseSettings
from typing import Optional

class DatasetConfig(BaseSettings):
    DATASET_NAME: str = "BIFOLD-BigEarthNetv2-0/BigEarthNet.txt"
    DATASET_MAX_PAIRS: int = 100
    DATASET_CACHE_DIR: str = "./data/cache"
    DATASET_OUTPUT_DIR: str = "./data/bigearthnet"
    DATASET_SEED: int = 42

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = DatasetConfig()
