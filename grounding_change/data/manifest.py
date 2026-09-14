"""
Dataset Manifest Management.
Generates and maintains datasets/manifest.json recording download status,
splits, file counts, and metadata for all change intelligence datasets.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatasetEntry(BaseModel):
    """Manifest record for a single dataset."""
    dataset: str
    source: str
    status: str = "missing"  # "complete", "partial", "missing"
    image_pairs: int = 0
    annotations: int = 0
    splits: Dict[str, int] = Field(default_factory=dict)
    classes: List[str] = Field(default_factory=list)
    license: str = "Research / Non-Commercial"
    download_timestamp: Optional[str] = None
    missing_files: List[str] = Field(default_factory=list)
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasetManifestManager:
    """Read, update, and validate the dataset manifest."""

    def __init__(self, manifest_path: Optional[Path] = None):
        if manifest_path is None:
            from ..config import settings
            manifest_path = settings.data.manifest_path
        self.manifest_path = Path(manifest_path)
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, DatasetEntry]:
        """Load manifest from disk or return empty defaults."""
        if not self.manifest_path.exists():
            return {}
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            entries = {}
            for name, data in raw.items():
                entries[name] = DatasetEntry(**data)
            return entries
        except Exception:
            return {}

    def save(self, entries: Dict[str, DatasetEntry]):
        """Save dataset entries to manifest.json."""
        serialized = {k: v.model_dump() for k, v in entries.items()}
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2)

    def update_dataset(
        self,
        dataset_name: str,
        source: str,
        status: str,
        image_pairs: int = 0,
        annotations: int = 0,
        splits: Optional[Dict[str, int]] = None,
        classes: Optional[List[str]] = None,
        license_name: str = "Research / Non-Commercial",
        missing_files: Optional[List[str]] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> DatasetEntry:
        """Update or create a dataset entry."""
        entries = self.load()
        entry = DatasetEntry(
            dataset=dataset_name,
            source=source,
            status=status,
            image_pairs=image_pairs,
            annotations=annotations,
            splits=splits or {},
            classes=classes or [],
            license=license_name,
            download_timestamp=datetime.utcnow().isoformat() + "Z",
            missing_files=missing_files or [],
            extra_metadata=extra_metadata or {}
        )
        entries[dataset_name] = entry
        self.save(entries)
        return entry

    def get_status(self, dataset_name: str) -> str:
        """Return status ('complete', 'partial', 'missing') of a dataset."""
        entries = self.load()
        if dataset_name in entries:
            return entries[dataset_name].status
        return "missing"
