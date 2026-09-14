"""
RSVLM-QA Dataset Downloader.
Source: https://huggingface.co/papers/2508.07918
Optional supplementary dataset for remote-sensing question diversity and scene understanding.
"""

from pathlib import Path
from typing import Any, Dict
from huggingface_hub import snapshot_download
from .base import DatasetDownloader


class RSVLMQADownloader(DatasetDownloader):
    """Downloader for RSVLM-QA supplementary remote-sensing benchmark."""

    @property
    def dataset_name(self) -> str:
        return "rsvlmqa"

    @property
    def official_source(self) -> str:
        return "https://huggingface.co/papers/2508.07918"

    @property
    def is_required(self) -> bool:
        return False

    def check_existing(self) -> bool:
        return len(list(self.target_dir.glob("*.*"))) > 0

    def download(self) -> bool:
        print(f"\nDownloading RSVLM-QA (Supplementary VQA dataset)...")
        try:
            snapshot_download(
                repo_id="rsvlm/RSVLM-QA",
                repo_type="dataset",
                local_dir=str(self.target_dir)
            )
        except Exception as e:
            print(f"RSVLM-QA note: {e}")

        val = self.validate()
        self.manifest_mgr.update_dataset(
            dataset_name=self.dataset_name,
            source=self.official_source,
            status="complete" if val.get("valid") else "missing",
            image_pairs=val.get("total_pairs", 0),
            annotations=val.get("total_annotations", 0),
            splits=val.get("splits", {}),
            license_name="Research Use Only"
        )
        return val.get("valid", False)

    def validate(self) -> Dict[str, Any]:
        count = len(list(self.target_dir.glob("**/*.*")))
        return {
            "dataset": self.dataset_name,
            "valid": count > 0,
            "total_pairs": count,
            "total_annotations": count,
            "splits": {"total": count}
        }
