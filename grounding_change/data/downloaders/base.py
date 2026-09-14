"""
Base class and utilities for dataset downloaders.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from tqdm import tqdm
from ..manifest import DatasetManifestManager


class DatasetDownloader(ABC):
    """Abstract dataset downloader with validation, resuming, and manifest updates."""

    def __init__(self, target_dir: Path, manifest_mgr: Optional[DatasetManifestManager] = None):
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_mgr = manifest_mgr or DatasetManifestManager()

    @property
    @abstractmethod
    def dataset_name(self) -> str:
        """Name of the dataset."""
        pass

    @property
    @abstractmethod
    def official_source(self) -> str:
        """URL or citation of official source."""
        pass

    @property
    def is_required(self) -> bool:
        """Whether this dataset is mandatory for full system functionality."""
        return False

    @abstractmethod
    def check_existing(self) -> bool:
        """Check if dataset files are already completely present."""
        pass

    @abstractmethod
    def download(self) -> bool:
        """Execute the download and preparation process."""
        pass

    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        """Validate files after download."""
        pass

    def download_file(self, url: str, dest_path: Path, chunk_size: int = 1024 * 1024) -> bool:
        """
        Download a single file over HTTP with resume capability and tqdm progress bar.
        """
        dest_path = Path(dest_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        resume_byte_pos = 0
        if dest_path.exists():
            resume_byte_pos = dest_path.stat().st_size

        headers = {}
        if resume_byte_pos > 0:
            headers["Range"] = f"bytes={resume_byte_pos}-"

        try:
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            if response.status_code == 416:
                # File already fully downloaded
                return True
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0)) + resume_byte_pos
            mode = "ab" if resume_byte_pos > 0 else "wb"

            with open(dest_path, mode) as f, tqdm(
                total=total_size,
                initial=resume_byte_pos,
                unit="B",
                unit_scale=True,
                desc=dest_path.name
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
            return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
