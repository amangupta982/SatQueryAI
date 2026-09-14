import time
from huggingface_hub import snapshot_download

repo_id = "IDEA-Research/grounding-dino-tiny"
max_retries = 10
retry_delay = 5

for attempt in range(max_retries):
    try:
        print(f"Attempt {attempt + 1}/{max_retries}: Downloading {repo_id}...")
        # snapshot_download will resume partially downloaded files automatically
        snapshot_download(repo_id=repo_id, resume_download=True)
        print("Download completed successfully!")
        break
    except Exception as e:
        print(f"Download failed with error: {e}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Failed to download model after maximum retries.")
