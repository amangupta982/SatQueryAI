"""
BigEarthNet.txt Dataset Downloader.
Paper: https://arxiv.org/abs/2603.29630
Multimodal remote-sensing VQA and domain adaptation benchmark.
Optional supplementary dataset.
"""

from pathlib import Path
from typing import Any, Dict
from huggingface_hub import snapshot_download
from .base import DatasetDownloader


class BigEarthNetDownloader(DatasetDownloader):
    """Downloader for BigEarthNet.txt remote-sensing VQA benchmark."""

    @property
    def dataset_name(self) -> str:
        return "bigearthnet"

    @property
    def official_source(self) -> str:
        return "https://arxiv.org/abs/2603.29630"

    @property
    def is_required(self) -> bool:
        return False

    def check_existing(self) -> bool:
        return len(list(self.target_dir.glob("*.*"))) > 0

    def download(self) -> bool:
        print(f"\nDownloading BigEarthNet.txt (Optional Multimodal RS dataset)...")
        try:
            snapshot_download(
                repo_id="bigearthnet/BigEarthNet-v1.0",
                repo_type="dataset",
                local_dir=str(self.target_dir),
                max_workers=2
            )
        except Exception as e:
            print(f"BigEarthNet download note: {e}")
            print(f"Refer to {self.official_source} for direct archive access.")

        val = self.validate()
        self.manifest_mgr.update_dataset(
            dataset_name=self.dataset_name,
            source=self.official_source,
            status="complete" if val.get("valid") else "missing",
            image_pairs=val.get("total_pairs", 0),
            annotations=val.get("total_annotations", 0),
            splits=val.get("splits", {}),
            license_name="CDLA-Permissive"
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
