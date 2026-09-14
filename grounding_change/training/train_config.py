"""
Training Configuration and Profile Specifications.
Enforces dataset-to-task mappings and profile validation.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TrainingProfileConfig(BaseModel):
    """Configuration for a specific training regimen."""
    profile_name: str
    required_datasets: List[str]
    active_heads: List[str]
    description: str


PROFILES: Dict[str, TrainingProfileConfig] = {
    "minimal": TrainingProfileConfig(
        profile_name="minimal",
        required_datasets=["second"],
        active_heads=["change_head", "semantic_head"],
        description="Minimal profile: trains binary and semantic change segmentation on SECOND."
    ),
    "vqa": TrainingProfileConfig(
        profile_name="vqa",
        required_datasets=["changechat", "rsrcc"],
        active_heads=["vqa_head"],
        description="VQA profile: trains interactive temporal VQA on ChangeChat-105k and RSRCC."
    ),
    "grounding": TrainingProfileConfig(
        profile_name="grounding",
        required_datasets=["qag360k"],
        active_heads=["grounding_head"],
        description="Grounding profile: trains query-conditioned localization on QAG-360K."
    ),
    "change": TrainingProfileConfig(
        profile_name="change",
        required_datasets=["second", "changechat"],
        active_heads=["change_head", "semantic_head", "vqa_head"],
        description="Change profile: joint perception and VQA on SECOND and ChangeChat."
    ),
    "full": TrainingProfileConfig(
        profile_name="full",
        required_datasets=["changechat", "rsrcc", "qag360k", "second"],
        active_heads=["change_head", "semantic_head", "transition_head", "grounding_head", "vqa_head"],
        description="Full multi-task profile: trains all heads jointly across all required datasets."
    ),
}
