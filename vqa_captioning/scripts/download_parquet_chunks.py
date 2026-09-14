#!/usr/bin/env python3
"""
Robust multi-chunk downloader for BigEarthNet.txt.parquet.
Downloads 32 isolated chunks in parallel with automatic resume and retries.
Assembles them into data/BigEarthNet.txt.parquet and validates with pyarrow.
"""

import os
import sys
import time
import shutil
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://huggingface.co/datasets/BIFOLD-BigEarthNetv2-0/BigEarthNet.txt/resolve/main/BigEarthNet.txt.parquet"
OUTPUT_FILE = Path("data/BigEarthNet.txt.parquet")
CHUNKS_DIR = Path("data/chunks")
NUM_CHUNKS = 32
MAX_WORKERS = 16

def get_content_length():
    resp = requests.head(URL, allow_redirects=True, timeout=20)
    return int(resp.headers.get("content-length", 466819745))

def download_chunk(chunk_id, start, end, chunk_file):
    expected_size = end - start + 1
    
    # Check if already fully downloaded
    if chunk_file.exists() and chunk_file.stat().st_size == expected_size:
        return chunk_id, expected_size, True

    session = requests.Session()
    for attempt in range(15):
        try:
            current_size = chunk_file.stat().st_size if chunk_file.exists() else 0
            if current_size == expected_size:
                return chunk_id, expected_size, True
            if current_size > expected_size:
                chunk_file.unlink()
                current_size = 0

            req_start = start + current_size
            headers = {
                "Range": f"bytes={req_start}-{end}",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            }

            with session.get(URL, headers=headers, stream=True, timeout=30, allow_redirects=True) as resp:
                if resp.status_code in (200, 206):
                    mode = "ab" if current_size > 0 else "wb"
                    with open(chunk_file, mode) as f:
                        for data in resp.iter_content(chunk_size=128 * 1024):
                            if data:
                                f.write(data)
                    
                    if chunk_file.stat().st_size == expected_size:
                        return chunk_id, expected_size, False
            time.sleep(1 + attempt)
        except Exception as e:
            time.sleep(2 + attempt)

    raise RuntimeError(f"Chunk {chunk_id} ({start}-{end}) failed after multiple attempts")

def main():
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Resolving dataset size for: {URL}", flush=True)
    total_size = get_content_length()
    print(f"Total size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)", flush=True)

    chunk_size = total_size // NUM_CHUNKS
    chunk_tasks = []
    for i in range(NUM_CHUNKS):
        start = i * chunk_size
        end = (start + chunk_size - 1) if i < NUM_CHUNKS - 1 else total_size - 1
        chunk_file = CHUNKS_DIR / f"chunk_{i:02d}.part"
        chunk_tasks.append((i, start, end, chunk_file))

    print(f"Launching {NUM_CHUNKS} chunks with {MAX_WORKERS} concurrent workers...", flush=True)
    t0 = time.time()
    completed_chunks = 0
    total_bytes_downloaded = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(download_chunk, cid, s, e, f): cid
            for cid, s, e, f in chunk_tasks
        }
        for fut in as_completed(futures):
            cid = futures[fut]
            try:
                chunk_id, nbytes, cached = fut.result()
                completed_chunks += 1
                total_bytes_downloaded += nbytes
                elapsed = time.time() - t0
                pct = (completed_chunks / NUM_CHUNKS) * 100
                mb_s = (total_bytes_downloaded / (1024*1024)) / max(elapsed, 0.1)
                cache_str = " (cached)" if cached else ""
                print(f"[{completed_chunks:02d}/{NUM_CHUNKS}] Chunk {chunk_id:02d} done{cache_str} ({nbytes/(1024*1024):.1f} MB) - Overall: {pct:.1f}% @ {mb_s:.2f} MB/s", flush=True)
            except Exception as exc:
                print(f"[ERROR] Chunk {cid} failed: {exc}", flush=True)
                sys.exit(1)

    print(f"\nAll {NUM_CHUNKS} chunks downloaded successfully in {time.time()-t0:.1f}s!", flush=True)
    print(f"Assembling chunks into {OUTPUT_FILE}...", flush=True)
    
    with open(OUTPUT_FILE, "wb") as outfile:
        for i in range(NUM_CHUNKS):
            part_path = CHUNKS_DIR / f"chunk_{i:02d}.part"
            with open(part_path, "rb") as infile:
                shutil.copyfileobj(infile, outfile, length=1024*1024)

    final_size = OUTPUT_FILE.stat().st_size
    print(f"Assembled {OUTPUT_FILE}: {final_size:,} bytes.", flush=True)
    assert final_size == total_size, f"Size mismatch: {final_size} vs {total_size}"

    # Verify with PyArrow
    print("Validating with PyArrow...", flush=True)
    import pyarrow.parquet as pq
    table = pq.read_table(str(OUTPUT_FILE))
    print(f"SUCCESS! Parquet verified: {table.num_rows:,} rows, {table.num_columns} columns.", flush=True)
    print("Columns:", table.column_names, flush=True)

if __name__ == "__main__":
    main()
