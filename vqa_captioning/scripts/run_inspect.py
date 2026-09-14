#!/usr/bin/env python3
"""
CLI script to inspect and audit BigEarthNet.txt or local remote-sensing dataset.
Usage:
    python vqa_captioning/scripts/run_inspect.py --dataset /path/to/BigEarthNet.txt [--skip-images]
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from vqa_captioning.preprocessing.dataset_inspector import DatasetInspector

def main():
    parser = argparse.ArgumentParser(description="Inspect BigEarthNet.txt dataset structure and quality.")
    parser.add_argument("--dataset", type=str, required=True, help="Path to BigEarthNet.txt directory or JSON file")
    parser.add_argument("--skip-images", action="store_true", help="Skip checking for image existence on disk")
    parser.add_argument("--output-report", type=str, default=None, help="Optional path to save markdown report")

    args = parser.parse_args()

    inspector = DatasetInspector(dataset_path=args.dataset, check_images=not args.skip_images)
    try:
        report = inspector.inspect()
        formatted_output = inspector.print_inspection_report(report)
        print(formatted_output)

        if args.output_report:
            out_path = Path(args.output_report)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(formatted_output)
            print(f"\nReport successfully saved to: {out_path}")

    except Exception as e:
        print(f"Error during inspection: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
