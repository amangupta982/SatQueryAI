"""
ChangeChat-105k Dataset Downloader.
Downloads instruction/dialogue annotations from Hugging Face (hlwu/changechat-105k)
and coordinates acquisition of official LEVIR-CC bitemporal imagery.
"""

from pathlib import Path
from typing import Any, Dict
from huggingface_hub import hf_hub_download, snapshot_download
from .base import DatasetDownloader
from ..validator import DatasetValidator


class ChangeChatDownloader(DatasetDownloader):
    """Downloader for ChangeChat-105k interactive change VQA dataset."""

    @property
    def dataset_name(self) -> str:
        return "changechat"

    @property
    def official_source(self) -> str:
        return "https://huggingface.co/datasets/hlwu/changechat-105k"

    @property
    def is_required(self) -> bool:
        return True

    def check_existing(self) -> bool:
        annos = list(self.target_dir.glob("*.json"))
        images = list(self.target_dir.glob("images/**/*.*")) + list(self.target_dir.glob("LEVIR-CC/**/*.*"))
        return len(annos) > 0 and len(images) > 0

    def download(self) -> bool:
        print(f"\n=======================================================")
        print(f"Downloading ChangeChat-105k Annotations from Hugging Face...")
        print(f"Source: {self.official_source}")
        print(f"=======================================================")

        try:
            # Download annotation JSON files
            repo_id = "hlwu/changechat-105k"
            snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                local_dir=str(self.target_dir),
                allow_patterns=["*.json", "*.md"]
            )
            print("Successfully downloaded ChangeChat-105k annotations.")
        except Exception as e:
            print(f"Warning/Error fetching from HF Hub: {e}")
            print("Trying direct raw download of primary instruction file...")
            raw_url = "https://huggingface.co/datasets/hlwu/changechat-105k/raw/main/changechat_105k_train.json"
            self.download_file(raw_url, self.target_dir / "changechat_105k_train.json")

        # Now check LEVIR-CC imagery
        levir_dir = self.target_dir / "LEVIR-CC"
        if not levir_dir.exists() and not (self.target_dir / "images").exists():
            print("\n-------------------------------------------------------")
            print("NOTE: ChangeChat-105k annotations reference LEVIR-CC bitemporal images.")
            print("Attempting to acquire LEVIR-CC images from public mirror...")
            try:
                # Try downloading from Hugging Face LEVIR-CC mirror
                snapshot_download(
                    repo_id="lcybuaa/LEVIR-CC",
                    repo_type="dataset",
                    local_dir=str(levir_dir),
                    allow_patterns=["*.png", "*.jpg", "images/*"]
                )
                print("LEVIR-CC images downloaded successfully.")
            except Exception as e:
                print(f"Automated LEVIR-CC download note: {e}")
                print("LEVIR-CC can be downloaded from official repository: https://github.com/Chen-Yang-Liu/LEVIR-CC-Dataset")
                print("Extract images into: datasets/changechat/images/")

        val = self.validate()
        self.manifest_mgr.update_dataset(
            dataset_name=self.dataset_name,
            source=self.official_source,
            status="complete" if val.get("valid") else "partial",
            image_pairs=val.get("total_pairs", 0),
            annotations=val.get("total_annotations", 0),
            splits=val.get("splits", {}),
            classes=["building", "vegetation", "water", "bare_land", "road"],
            license_name="Research Use Only"
        )
        return val.get("valid", False)

    def validate(self) -> Dict[str, Any]:
        result = DatasetValidator.validate_changechat(self.target_dir)
        return result.to_dict()
