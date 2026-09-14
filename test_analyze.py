import time
print("Starting analysis...")
from PIL import Image
from area_measurement.inference import analyze_area

img = Image.open("/Users/rohan/.gemini/antigravity-ide/brain/fab7e122-9c56-4701-95a2-f5b8b9330562/.tempmediaStorage/media_1789148288938.png").convert("RGB")

print("Running analyze_area(force_satellite_mode=True)...")
start = time.time()
res = analyze_area(img, force_satellite_mode=True)
print(f"Finished in {time.time() - start:.2f}s")
print("Classes found:", len(res["classes"]))
