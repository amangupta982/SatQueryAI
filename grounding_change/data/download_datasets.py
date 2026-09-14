"""
Dataset Acquisition CLI for SatQueryAI Grounding & Change Intelligence.
Command-line interface to download, unpack, validate, and catalog datasets.

Usage:
  python -m grounding_change.data.download_datasets --all
  python -m grounding_change.data.download_datasets --required
  python -m grounding_change.data.download_datasets --profile full
  python -m grounding_change.data.download_datasets --dataset changechat
  python -m grounding_change.data.download_datasets --dataset second
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Type

from ..config import settings
from .manifest import DatasetManifestManager
from .downloaders.base import DatasetDownloader
from .downloaders.changechat import ChangeChatDownloader
from .downloaders.rsrcc import RSRCCDownloader
from .downloaders.second import SECONDDownloader
from .downloaders.qag360k import QAG360KDownloader
from .downloaders.bigearthnet import BigEarthNetDownloader
from .downloaders.rsvlmqa import RSVLMQADownloader


DOWNLOADER_REGISTRY: Dict[str, Tuple[Type[DatasetDownloader], Path]] = {
    "changechat": (ChangeChatDownloader, settings.data.changechat_dir),
    "rsrcc": (RSRCCDownloader, settings.data.rsrcc_dir),
    "qag360k": (QAG360KDownloader, settings.data.qag360k_dir),
    "second": (SECONDDownloader, settings.data.second_dir),
    "bigearthnet": (BigEarthNetDownloader, settings.data.bigearthnet_dir),
    "rsvlmqa": (RSVLMQADownloader, settings.data.rsvlmqa_dir),
}

REQUIRED_DATASETS = ["changechat", "rsrcc", "qag360k", "second"]

PROFILE_MAPPING = {
    "minimal": ["second"],
    "vqa": ["changechat", "rsrcc"],
    "grounding": ["qag360k"],
    "change": ["second", "changechat"],
    "full": ["changechat", "rsrcc", "qag360k", "second", "bigearthnet", "rsvlmqa"],
}


def run_downloader(dataset_name: str, manifest_mgr: DatasetManifestManager) -> bool:
    """Instantiate and run a specific dataset downloader."""
    if dataset_name not in DOWNLOADER_REGISTRY:
        print(f"Error: Unknown dataset '{dataset_name}'. Available: {list(DOWNLOADER_REGISTRY.keys())}")
        return False

    cls, target_dir = DOWNLOADER_REGISTRY[dataset_name]
    downloader = cls(target_dir=target_dir, manifest_mgr=manifest_mgr)
    print(f"\n>>> Running acquisition for: {dataset_name.upper()}...")
    success = downloader.download()
    status = "SUCCESS" if success else "ACTION REQUIRED / PARTIAL"
    print(f">>> Result for {dataset_name.upper()}: {status}")
    return success


def print_readiness_report(manifest_mgr: DatasetManifestManager):
    """Print standard readiness report across all managed datasets."""
    entries = manifest_mgr.load()
    print("\n" + "=" * 65)
    print("        SATQUERY-AI DATASET READINESS REPORT")
    print("=" * 65)

    all_keys = list(DOWNLOADER_REGISTRY.keys())
    for name in all_keys:
        entry = entries.get(name)
        is_req = name in REQUIRED_DATASETS
        req_tag = "REQUIRED" if is_req else "OPTIONAL"

        if entry and entry.status == "complete":
            status_str = "READY"
        elif entry and entry.status == "partial":
            status_str = "PARTIAL"
        else:
            status_str = "MISSING"

        print(f"  {name.upper():<14} : {status_str:<10} [{req_tag}]")
        if entry:
            print(f"     Pairs: {entry.image_pairs}, Annotations: {entry.annotations}")
            if entry.splits:
                print(f"     Splits: {entry.splits}")

    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="SatQueryAI Dataset Acquisition Manager")
    parser.add_argument("--all", action="store_true", help="Download all known datasets")
    parser.add_argument("--required", action="store_true", help="Download required datasets (ChangeChat, RSRCC, QAG-360K, SECOND)")
    parser.add_argument("--profile", choices=list(PROFILE_MAPPING.keys()), help="Download by training profile")
    parser.add_argument("--dataset", choices=list(DOWNLOADER_REGISTRY.keys()), help="Download a specific dataset")
    parser.add_argument("--report", action="store_true", help="Print dataset readiness report only")

    args = parser.parse_args()
    manifest_mgr = DatasetManifestManager()

    if args.report:
        print_readiness_report(manifest_mgr)
        return

    targets: List[str] = []
    if args.all:
        targets = list(DOWNLOADER_REGISTRY.keys())
    elif args.required:
        targets = REQUIRED_DATASETS
    elif args.profile:
        targets = PROFILE_MAPPING[args.profile]
    elif args.dataset:
        targets = [args.dataset]
    else:
        # Default behavior: report status
        print_readiness_report(manifest_mgr)
        print("Run with --required, --all, --profile full, or --dataset <name> to initiate download.")
        return

    print(f"Starting dataset acquisition for: {', '.join(targets)}")
    for name in targets:
        run_downloader(name, manifest_mgr)

    print_readiness_report(manifest_mgr)


if __name__ == "__main__":
    main()
