#!/usr/bin/env python3
"""
Parallel downloader for real Sentinel-2 RGB satellite image patches into data/images/.
Uses ThreadPoolExecutor for fast concurrent downloads.
"""

import os
import io
import json
import time
import requests
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

IMAGES_DIR = Path("data/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

METADATA_URL = "https://huggingface.co/datasets/sshh12/sentinel-2-rgb-captioned/resolve/main/train/images/metadata.jsonl"
BASE_IMG_URL = "https://huggingface.co/datasets/sshh12/sentinel-2-rgb-captioned/resolve/main/train/images"

def download_single_image(item):
    fname = item["file_name"]
    out_path = IMAGES_DIR / fname
    if out_path.exists() and out_path.stat().st_size > 1000:
        return fname, True, "exists"

    img_url = f"{BASE_IMG_URL}/{fname}"
    for _ in range(3):
        try:
            resp = requests.get(img_url, timeout=12)
            if resp.status_code == 200:
                with Image.open(io.BytesIO(resp.content)) as im:
                    im_120 = im.convert("RGB").resize((120, 120), Image.Resampling.LANCZOS)
                    im_120.save(out_path, format="PNG", optimize=True)
                return fname, True, item.get("text", "")
        except Exception:
            time.sleep(1)
    return fname, False, "failed"

def main(target_count=60):
    print(f"Fetching Sentinel-2 catalog...", flush=True)
    r = requests.get(METADATA_URL, timeout=15)
    lines = [line for line in r.text.strip().split("\n") if line.strip()]
    records = [json.loads(line) for line in lines]

    categories = ["forest", "ocean", "coastline", "grassland", "prairie", "desert", "delta", "island", "mountain", "steppe"]
    grouped = {}
    for rec in records:
        text = rec["text"]
        for cat in categories:
            if cat in text:
                grouped.setdefault(cat, []).append(rec)
                break

    download_list = []
    idx = 0
    while len(download_list) < target_count:
        added = False
        for cat in categories:
            items = grouped.get(cat, [])
            if idx < len(items):
                download_list.append(items[idx])
                added = True
                if len(download_list) >= target_count:
                    break
        if not added:
            break
        idx += 1

    print(f"Downloading {len(download_list)} Sentinel-2 images using 8 concurrent workers...", flush=True)
    t0 = time.time()
    downloaded = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(download_single_image, item) for item in download_list]
        for fut in as_completed(futures):
            fname, success, msg = fut.result()
            if success:
                downloaded += 1
                if downloaded % 5 == 0 or downloaded == len(download_list):
                    print(f"[{downloaded}/{len(download_list)}] Downloaded {fname} ({msg})", flush=True)

    print(f"Done! {downloaded} real Sentinel-2 images stored in {IMAGES_DIR} in {time.time()-t0:.1f}s.", flush=True)

if __name__ == "__main__":
    main()
