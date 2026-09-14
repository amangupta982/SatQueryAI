"""
QAG-360K / VisTA Dataset Downloader.
Official repository: https://github.com/like413/VisTA
ArXiv: https://arxiv.org/abs/2410.23828
Primary source for visual grounding: Question + Answer + Grounding Mask.
"""

from pathlib import Path
from typing import Any, Dict
from huggingface_hub import snapshot_download
from .base import DatasetDownloader
from ..validator import DatasetValidator


class QAG360KDownloader(DatasetDownloader):
    """Downloader for VisTA / QAG-360K visual grounding benchmark."""

    @property
    def dataset_name(self) -> str:
        return "qag360k"

    @property
    def official_source(self) -> str:
        return "https://github.com/like413/VisTA"

    @property
    def is_required(self) -> bool:
        return True

    def check_existing(self) -> bool:
        items = list(self.target_dir.glob("*.json")) + list(self.target_dir.glob("masks/*"))
        return len(items) > 0

    def download(self) -> bool:
        print(f"\n=======================================================")
        print(f"Acquiring VisTA QAG-360K Visual Grounding Dataset...")
        print(f"Official Source: {self.official_source}")
        print(f"=======================================================")

        try:
            # Check for VisTA public repository on HF Hub
            snapshot_download(
                repo_id="like413/VisTA-QAG360K",
                repo_type="dataset",
                local_dir=str(self.target_dir)
            )
            print("Successfully acquired QAG-360K files from repository.")
        except Exception as e:
            print(f"Direct HF snapshot notice: {e}")
            print("\n-------------------------------------------------------")
            print("QAG-360K ACCESS INSTRUCTIONS:")
            print(f"Visit: {self.official_source}")
            print("Follow the VisTA data release instructions for QAG-360K grounding annotations.")
            print(f"Place dataset files in: {self.target_dir.resolve()}")
            print("-------------------------------------------------------\n")

        val = self.validate()
        status = "complete" if val.get("valid") else "partial"
        self.manifest_mgr.update_dataset(
            dataset_name=self.dataset_name,
            source=self.official_source,
            status=status,
            image_pairs=val.get("total_pairs", 0),
            annotations=val.get("total_annotations", 0),
            splits=val.get("splits", {}),
            classes=["building", "vegetation", "water", "road", "bare_land", "cropland", "bridge", "port", "airport", "stadium"],
            license_name="Non-Commercial Research Use Only"
        )
        return val.get("valid", False)

    def validate(self) -> Dict[str, Any]:
        result = DatasetValidator.validate_qag360k(self.target_dir)
        return result.to_dict()
