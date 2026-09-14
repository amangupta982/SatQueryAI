import time
print("Importing GroundingEngine...")
from grounding.inference import GroundingEngine

print("Instantiating GroundingEngine...")
start = time.time()
engine = GroundingEngine.get_instance()
print(f"Instantiated in {time.time() - start:.2f} seconds.")
