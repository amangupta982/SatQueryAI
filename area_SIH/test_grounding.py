from PIL import Image
import os
import time

try:
    from grounding.api import ground_objects

    print("Testing Grounding Module...")
    
    # Create dummy white image
    img = Image.new('RGB', (400, 400), color='white')
    
    # Run query
    print("Running query: 'Where are the buildings?'")
    result = ground_objects(img, "Where are the buildings?")
    
    print("Detections:")
    print(result["detections"])
    print(f"Processing time: {result['processing_time']:.2f}s")
    
    print("Test passed.")
    
except Exception as e:
    print(f"Test failed: {e}")
