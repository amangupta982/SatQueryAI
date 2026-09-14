from huggingface_hub import hf_hub_download
import time

repo_id = "IDEA-Research/grounding-dino-tiny"
files_to_download = [
    "model.safetensors",
    "preprocessor_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "vocab.txt"
]

for filename in files_to_download:
    success = False
    for attempt in range(5):
        try:
            print(f"Downloading {filename} (Attempt {attempt+1}/5)...")
            hf_hub_download(repo_id=repo_id, filename=filename, resume_download=True)
            print(f"Successfully downloaded {filename}!")
            success = True
            break
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            time.sleep(3)
    if not success:
        print(f"Gave up on {filename}")
