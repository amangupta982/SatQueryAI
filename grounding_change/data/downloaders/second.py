"""
SECOND Dataset Downloader.
Semantic Change Detection dataset from Wuhan University.
Provides pixel-level semantic change supervision across 6 land-cover categories.
"""

from pathlib import Path
from typing import Any, Dict
from huggingface_hub import snapshot_download
from .base import DatasetDownloader
from ..validator import DatasetValidator


class SECONDDownloader(DatasetDownloader):
    """Downloader and unpacker for SECOND semantic change detection benchmark."""

    @property
    def dataset_name(self) -> str:
        return "second"

    @property
    def official_source(self) -> str:
        return "http://www.captain-whu.com/project/SCD_SECOND.html"

    @property
    def is_required(self) -> bool:
        return True

    def check_existing(self) -> bool:
        im1 = list(self.target_dir.glob("**/im1/*.*"))
        im2 = list(self.target_dir.glob("**/im2/*.*"))
        return len(im1) > 0 and len(im2) > 0

    def download(self) -> bool:
        print(f"\n=======================================================")
        print(f"Acquiring SECOND Semantic Change Detection Dataset...")
        print(f"Official Source: {self.official_source}")
        print(f"=======================================================")

        # Check if already present
        if self.check_existing():
            print("SECOND dataset already detected on disk.")
            val = self.validate()
            self.manifest_mgr.update_dataset(
                dataset_name=self.dataset_name,
                source=self.official_source,
                status="complete",
                image_pairs=val.get("total_pairs", 0),
                annotations=val.get("total_annotations", 0),
                splits=val.get("splits", {}),
                classes=["non-vegetated ground", "tree", "low vegetation", "water", "building", "playground"],
                license_name="Academic Research Use Only"
            )
            return True

        # Attempt to pull from community mirror on Hugging Face Hub if available
        hf_mirrors = ["RSdata/SECOND", "WHU-SCD/SECOND"]
        downloaded = False
        for repo in hf_mirrors:
            try:
                print(f"Trying public repository mirror: {repo}...")
                snapshot_download(
                    repo_id=repo,
                    repo_type="dataset",
                    local_dir=str(self.target_dir),
                    max_workers=4
                )
                downloaded = True
                print(f"Successfully downloaded from {repo}")
                break
            except Exception as e:
                print(f"Mirror {repo} unavailable: {e}")

        if not downloaded:
            print("\n" + "!" * 60)
            print("MANUAL ACTION REQUIRED FOR SECOND DATASET:")
            print("The official SECOND benchmark is hosted by Wuhan University Captain Group.")
            print("Official portal: http://www.captain-whu.com/project/SCD_SECOND.html")
            print("Alternative Baidu/Google Drive links are provided on the official page.")
            print(f"Please place extracted files under: {self.target_dir.resolve()}")
            print("Expected directory structure:")
            print("  datasets/second/train/im1/")
            print("  datasets/second/train/im2/")
            print("  datasets/second/train/label1/")
            print("  datasets/second/train/label2/")
            print("  datasets/second/val/im1/ ...")
            print("!" * 60 + "\n")

        val = self.validate()
        status = "complete" if val.get("valid") else "missing"
        self.manifest_mgr.update_dataset(
            dataset_name=self.dataset_name,
            source=self.official_source,
            status=status,
            image_pairs=val.get("total_pairs", 0),
            annotations=val.get("total_annotations", 0),
            splits=val.get("splits", {}),
            classes=["non-vegetated ground", "tree", "low vegetation", "water", "building", "playground"],
            license_name="Academic Research Use Only"
        )
        return val.get("valid", False)

    def validate(self) -> Dict[str, Any]:
        result = DatasetValidator.validate_second(self.target_dir)
        return result.to_dict()
