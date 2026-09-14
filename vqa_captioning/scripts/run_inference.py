#!/usr/bin/env python3
"""
CLI script to run inference with SatQuery-VQA on a satellite image and question.
Usage:
    python vqa_captioning/scripts/run_inference.py --image /path/to/image.png --question "Is water present?"
"""

import sys
import argparse
import json
from pathlib import Path
from PIL import Image

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from vqa_captioning.inference.predictor import SatQueryPredictor

def main():
    parser = argparse.ArgumentParser(description="Run SatQuery-VQA inference on an image and question.")
    parser.add_argument("--image", type=str, required=False, default=None, help="Path to satellite image file")
    parser.add_argument("--question", type=str, required=True, help="Natural language question")
    parser.add_argument("--sensor", type=str, default="Sentinel-2", help="Sensor modality: Sentinel-2 or Sentinel-1")
    parser.add_argument("--adapter", type=str, default=None, help="Optional path to fine-tuned LoRA adapter")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode for fast local verification")

    args = parser.parse_args()

    predictor = SatQueryPredictor(
        adapter_path=args.adapter,
        mock_mode=args.mock,
    )

    img_input = args.image
    if img_input is None or not Path(img_input).exists():
        # Generate a 120x120 synthetic test image if no image path provided
        print("Note: No image path provided or file missing. Using synthetic 120x120 test scene.")
        img_input = Image.new("RGB", (120, 120), color=(40, 120, 180))

    result = predictor.ask(
        image=img_input,
        question=args.question,
        sensor=args.sensor,
    )

    print("\n" + "=" * 50)
    print("           SATQUERY-VQA INFERENCE RESULT           ")
    print("=" * 50)
    print(f"Question   : {args.question}")
    print(f"Answer     : {result.get('answer')}")
    print(f"Confidence : {result.get('confidence')}")
    print(f"Task       : {result.get('task')}")
    print(f"Model      : {result.get('model')}")
    if result.get("evidence"):
        print(f"Evidence   : {json.dumps(result.get('evidence'), indent=2)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
