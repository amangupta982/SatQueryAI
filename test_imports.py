import sys
import time

print("Starting test...")
start = time.time()
print("Importing torch...")
import torch
print(f"Torch imported in {time.time() - start:.2f}s")

start = time.time()
print("Importing torchvision...")
import torchvision
print(f"Torchvision imported in {time.time() - start:.2f}s")

start = time.time()
print("Importing analyze_area...")
from area_measurement.inference import analyze_area
print(f"analyze_area imported in {time.time() - start:.2f}s")

print("Done.")
