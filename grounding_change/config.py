"""
Configuration module for grounding_change.
Manages dataset paths, checkpoints, model parameters, and runtime settings.
"""

from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_ROOT / "datasets"
CHECKPOINT_DIR = MODULE_ROOT / "checkpoints"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Ensure runtime directories exist
DATA_ROOT.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class DatasetConfig(BaseModel):
    """Configuration for BigEarthNet.txt dataset locations and options."""
    root_dir: Path = DATA_ROOT
    dataset_name: str = "BigEarthNet.txt"
    dataset_paper: str = "https://arxiv.org/abs/2603.29630"
    official_source: str = "https://txt.bigearth.net/"
    hf_repo_id: str = "BIFOLD-BigEarthNetv2-0/BigEarthNet.txt"
    license: str = "CDLA-Permissive-1.0"
    
    # Strictly isolated local storage structure
    bigearthnet_txt_dir: Path = DATA_ROOT / "bigearthnet_txt"
    sentinel2_dir: Path = DATA_ROOT / "bigearthnet_txt" / "sentinel2"
    sentinel1_dir: Path = DATA_ROOT / "bigearthnet_txt" / "sentinel1"
    annotations_dir: Path = DATA_ROOT / "bigearthnet_txt" / "annotations"
    vqa_dir: Path = DATA_ROOT / "bigearthnet_txt" / "annotations" / "vqa"
    captions_dir: Path = DATA_ROOT / "bigearthnet_txt" / "annotations" / "captions"
    grounding_dir: Path = DATA_ROOT / "bigearthnet_txt" / "annotations" / "grounding"
    spatial_dir: Path = DATA_ROOT / "bigearthnet_txt" / "annotations" / "spatial"
    metadata_dir: Path = DATA_ROOT / "bigearthnet_txt" / "metadata"
    manifest_path: Path = DATA_ROOT / "bigearthnet_txt" / "manifest.json"


class ModelConfig(BaseModel):
    """Foundation architecture hyperparameters for Optical-SAR Multimodal Agent."""
    # Legacy / Siamese compatibility
    backbone: str = "resnet50"
    pretrained: bool = False
    img_size: int = 512
    in_channels: int = 3

    # Optical foundation encoder
    optical_backbone: str = "Prithvi-EO-2.0-300M"
    optical_bands: List[str] = ["B02", "B03", "B04", "B8A", "B11", "B12"]
    optical_in_channels: int = 6
    optical_img_size: int = 224
    
    # SAR foundation encoder
    sar_backbone: str = "SUMMIT"
    sar_polarizations: List[str] = ["VV", "VH"]
    sar_in_channels: int = 2
    sar_img_size: int = 224
    
    # Multimodal fusion & attention
    feature_dim: int = 256
    hidden_dim: int = 512
    cross_attention_heads: int = 8
    dropout: float = 0.1
    
    # Task heads (BigEarthNet.txt 15 tasks)
    num_semantic_classes: int = 7  # Extensible via taxonomy registry
    num_vqa_answers: int = 1000
    change_threshold: float = 0.5
    min_region_area: int = 16  # Minimum pixel area for a valid region


class TrainingConfig(BaseModel):
    """BigEarthNet.txt multi-stage training profile and hyperparameters."""
    profile: str = "multimodal_vqa_grounding"
    # Supported stages:
    # 1: Optical understanding
    # 2: SAR understanding
    # 3: Optical-SAR fusion
    # 4: BigEarthNet.txt VQA
    # 5: BigEarthNet.txt Grounding
    # 6: Multimodal VQA + Grounding
    # 7: Cross-modal reasoning
    # 8: Temporal reasoning (only where metadata establishes time difference)
    current_stage: int = 6
    epochs: int = 50
    batch_size: int = 8
    lr: float = 1e-4
    weight_decay: float = 1e-4
    lambda_optical: float = 1.0
    lambda_sar: float = 1.0
    lambda_fusion: float = 0.8
    lambda_vqa: float = 0.8
    lambda_grounding: float = 0.8
    lambda_semantic: float = 0.6
    device: str = "auto"
    num_workers: int = 2
    save_interval: int = 5


class GroundingChangeSettings(BaseModel):
    """Master configuration for the grounding_change module."""
    data: DatasetConfig = Field(default_factory=DatasetConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    training: TrainingConfig = Field(default_factory=TrainingConfig)


settings = GroundingChangeSettings()
