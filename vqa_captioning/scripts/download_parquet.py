#!/usr/bin/env python3
"""
Fast parallel range downloader for BigEarthNet.txt.parquet from Hugging Face.
Uses 8 concurrent HTTP range requests with automatic URL refresh and chunk retries.
"""

import os
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://huggingface.co/datasets/BIFOLD-BigEarthNetv2-0/BigEarthNet.txt/resolve/main/BigEarthNet.txt.parquet"
OUTPUT_FILE = "data/BigEarthNet.txt.parquet"
NUM_WORKERS = 8

def get_fresh_url():
    session = requests.Session()
    resp = session.head(URL, allow_redirects=True, timeout=20)
    return resp.url, int(resp.headers.get("content-length", 466819745))

def download_range(start, end, chunk_id, file_path):
    headers = {"Range": f"bytes={start}-{end}"}
    for attempt in range(8):
        try:
            url, _ = get_fresh_url()
            with requests.get(url, headers=headers, stream=True, timeout=45) as r:
                if r.status_code in [200, 206]:
                    with open(file_path, "r+b") as f:
                        f.seek(start)
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                    return chunk_id, end - start + 1
            time.sleep(2)
        except Exception as e:
            time.sleep(2)
    raise RuntimeError(f"Failed range {start}-{end} after 8 attempts")

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    print(f"Connecting to Hugging Face dataset: {URL}", flush=True)
    _, total_size = get_fresh_url()
    print(f"File size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)", flush=True)
    
    # Pre-allocate file if not right size
    if not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) != total_size:
        with open(OUTPUT_FILE, "wb") as f:
            f.truncate(total_size)
    
    chunk_size = total_size // NUM_WORKERS
    ranges = []
    for i in range(NUM_WORKERS):
        start = i * chunk_size
        end = (start + chunk_size - 1) if i < NUM_WORKERS - 1 else total_size - 1
        ranges.append((start, end, i))
    
    print(f"Starting parallel range download with {NUM_WORKERS} workers...", flush=True)
    t0 = time.time()
    completed_bytes = 0
    
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {
            executor.submit(download_range, start, end, idx, OUTPUT_FILE): (idx, end - start + 1)
            for start, end, idx in ranges
        }
        for fut in as_completed(futures):
            chunk_id, nbytes = fut.result()
            completed_bytes += nbytes
            elapsed = time.time() - t0
            pct = (completed_bytes / total_size) * 100
            speed = (completed_bytes / (1024*1024)) / max(elapsed, 0.1)
            print(f"Worker {chunk_id+1}/{NUM_WORKERS} complete! Overall: {pct:5.1f}% ({completed_bytes/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB) - {speed:.2f} MB/s", flush=True)
            
    print(f"\nSuccessfully downloaded and assembled {OUTPUT_FILE} ({total_size:,} bytes) in {time.time()-t0:.2f}s!", flush=True)

if __name__ == "__main__":
    main()
