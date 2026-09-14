#!/usr/bin/env python3
"""
CLI script to evaluate SatQuery-VQA or base VLM on BigEarthNet.txt benchmark splits.
Usage:
    python vqa_captioning/scripts/run_evaluate.py --split data/prepared_satquery_vqa/benchmark.json
"""

import sys
import argparse
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from vqa_captioning.evaluation.evaluate_vqa import VQAEvaluator

def main():
    parser = argparse.ArgumentParser(description="Evaluate SatQuery-VQA on BigEarthNet benchmark data.")
    parser.add_argument("--split", type=str, required=True, help="Path to evaluation JSON split (e.g. benchmark.json)")
    parser.add_argument("--adapter", type=str, default="models/satquery-vqa/adapter", help="Path to fine-tuned LoRA adapter")
    parser.add_argument("--max-samples", type=int, default=None, help="Limit number of samples evaluated")
    parser.add_argument("--output-report", type=str, default=None, help="Save markdown report to file")

    args = parser.parse_args()

    evaluator = VQAEvaluator(
        adapter_path=args.adapter,
    )

    print(f"Starting evaluation on {args.split}...")
    results = evaluator.evaluate_split(args.split, max_samples=args.max_samples)
    report_md = evaluator.generate_markdown_report(results)
    print("\n" + report_md)

    if args.output_report:
        out_path = Path(args.output_report)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"\nReport saved to: {out_path}")

if __name__ == "__main__":
    main()
