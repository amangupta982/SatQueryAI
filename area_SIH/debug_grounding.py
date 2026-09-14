import sys
import traceback
from PIL import Image
import torch

print("Python version:", sys.version)
print("Torch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

try:
    print("\n--- Testing transformers pipeline with IDEA-Research/grounding-dino-tiny ---")
    from transformers import pipeline
    pipe = pipeline("zero-shot-object-detection", model="IDEA-Research/grounding-dino-tiny", device=-1)
    img = Image.new('RGB', (300, 300), color='blue')
    res = pipe(img, candidate_labels=["water", "building"])
    print("Success with grounding-dino-tiny! Result:", res)
except Exception as e:
    print("Error with grounding-dino-tiny:")
    traceback.print_exc()

try:
    print("\n--- Testing transformers AutoProcessor + AutoModelForZeroShotObjectDetection with IDEA-Research/grounding-dino-tiny ---")
    from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
    model_id = "IDEA-Research/grounding-dino-tiny"
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
    print("Success loading AutoModelForZeroShotObjectDetection!")
except Exception as e:
    print("Error with AutoModelForZeroShotObjectDetection:")
    traceback.print_exc()

try:
    print("\n--- Testing transformers pipeline with google/owlvit-base-patch32 ---")
    pipe = pipeline("zero-shot-object-detection", model="google/owlvit-base-patch32", device=-1)
    img = Image.new('RGB', (300, 300), color='green')
    res = pipe(img, candidate_labels=["forest", "field"])
    print("Success with owlvit-base-patch32! Result:", res)
except Exception as e:
    print("Error with owlvit-base-patch32:")
    traceback.print_exc()
