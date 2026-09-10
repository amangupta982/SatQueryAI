import os
import json
import logging
from abc import ABC, abstractmethod
from typing import List

logger = logging.getLogger(__name__)

class ImageDownloader(ABC):
    @abstractmethod
    def download_pair(self, output_dir: str, optical_path: str, sar_path: str):
        pass

class MockDownloader(ImageDownloader):
    """
    A placeholder downloader that creates dummy files instead of actually downloading.
    Used for testing the pipeline when actual image URLs/archives are unavailable.
    """
    def download_pair(self, output_dir: str, optical_path: str, sar_path: str):
        opt_full = os.path.join(output_dir, optical_path)
        sar_full = os.path.join(output_dir, sar_path)
        
        # Create directories
        os.makedirs(os.path.dirname(opt_full), exist_ok=True)
        os.makedirs(os.path.dirname(sar_full), exist_ok=True)
        
        # Create dummy files
        if not os.path.exists(opt_full):
            with open(opt_full, 'w') as f:
                f.write("DUMMY OPTICAL RASTER DATA")
        
        if not os.path.exists(sar_full):
            with open(sar_full, 'w') as f:
                f.write("DUMMY SAR RASTER DATA")

def download_images_for_manifest(manifest_path: str, output_dir: str, downloader: ImageDownloader):
    """
    Reads the manifest and downloads required images.
    """
    if not os.path.exists(manifest_path):
        logger.error(f"Manifest not found: {manifest_path}")
        return

    download_count = 0
    skip_count = 0
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            opt_path = record['optical_path']
            sar_path = record['sar_path']
            
            opt_full = os.path.join(output_dir, opt_path)
            sar_full = os.path.join(output_dir, sar_path)
            
            if os.path.exists(opt_full) and os.path.exists(sar_full):
                skip_count += 1
            else:
                downloader.download_pair(output_dir, opt_path, sar_path)
                download_count += 1
                
    logger.info(f"Downloaded {download_count} new image pairs. Skipped {skip_count} existing.")
