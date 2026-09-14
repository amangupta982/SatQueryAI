import os
from huggingface_hub import snapshot_download

print("Downloading Qwen2.5-VL-3B-Instruct...")
snapshot_download(
    repo_id="Qwen/Qwen2.5-VL-3B-Instruct",
    allow_patterns=["*.safetensors", "*.json", "*.txt"],
    resume_download=True,
    max_workers=4
)
print("Qwen downloaded successfully!")
