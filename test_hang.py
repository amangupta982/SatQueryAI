import time
import torch

print("Before device initialization...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

print("Importing Segmenter...")
from area_measurement.segmentation import SemanticSegmenter

print("Instantiating segmenter...")
segmenter = SemanticSegmenter()
print("Segmenter instantiated!")

import numpy as np
img = np.zeros((100, 100, 3), dtype=np.uint8)

print("Running segment(use_satellite_mode=True)...")
segmenter.segment(img, use_satellite_mode=True)
print("Done!")
