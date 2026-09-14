"""
RSRCC (Remote Sensing Regional Change Comprehension) Dataset Downloader.
Official Google Research dataset for localized, fine-grained change VQA.
Source: https://github.com/google-research/remote-sensing / HF: google/RSRCC
"""

from pathlib import Path
from typing import Any, Dict
from huggingface_hub import snapshot_download
from .base import DatasetDownloader
from ..validator import DatasetValidator


class RSRCCDownloader(DatasetDownloader):
    """Downloader for Google RSRCC regional change QA dataset."""

    @property
    def dataset_name(self) -> str:
        return "rsrcc"

    @property
    def official_source(self) -> str:
        return "https://github.com/google-research/remote-sensing"

    @property
    def is_required(self) -> bool:
        return True

    def check_existing(self) -> bool:
        items = list(self.target_dir.glob("*.json")) + list(self.target_dir.glob("*.parquet"))
        return len(items) > 0

    def download(self) -> bool:
        print(f"\n=======================================================")
        print(f"Downloading Google RSRCC Dataset...")
        print(f"Source: {self.official_source}")
        print(f"=======================================================")

        try:
            snapshot_download(
                repo_id="google/RSRCC",
                repo_type="dataset",
                local_dir=str(self.target_dir)
            )
            print("Successfully downloaded RSRCC dataset via Hugging Face Hub.")
        except Exception as e:
            print(f"HF Hub download note for google/RSRCC: {e}")
            print("Attempting official Google Research repository retrieval...")
            git_url = "https://raw.githubusercontent.com/google-research/remote-sensing/main/README.md"
            self.download_file(git_url, self.target_dir / "README.md")

        val = self.validate()
        self.manifest_mgr.update_dataset(
            dataset_name=self.dataset_name,
            source=self.official_source,
            status="complete" if val.get("valid") else "partial",
            image_pairs=val.get("total_pairs", 0),
            annotations=val.get("total_annotations", 0),
            splits=val.get("splits", {}),
            classes=["building", "vegetation", "water", "bare_land", "road"],
            license_name="Apache-2.0"
        )
        return val.get("valid", False)

    def validate(self) -> Dict[str, Any]:
        result = DatasetValidator.validate_rsrcc(self.target_dir)
        return result.to_dict()
