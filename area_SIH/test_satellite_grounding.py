from PIL import Image
import os
from grounding.api import ground_objects
from grounding.inference import GroundingModel

img_path = "sample_images/sample1.jpeg"
if not os.path.exists(img_path):
    img_path = "sample_images/sample2.jpeg"

img = Image.open(img_path).convert("RGB")
print(f"Loaded image {img_path}, size={img.size}")

queries = ["building", "water", "greenery", "bridge", "road", "Where are the buildings?"]

for q in queries:
    print(f"\n================ Query: '{q}' ================")
    # Test with threshold 0.15
    res = ground_objects(img, q, box_threshold=0.15)
    dets = res["detections"]
    print(f"Found {len(dets)} detections at threshold=0.15 in {res['processing_time']:.2f}s:")
    for d in dets[:5]:
        print("  -", d["label"], "score:", round(d["score"], 3), "box:", d["box"])
