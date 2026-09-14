#!/usr/bin/env python3
"""
CLI script to train SatQuery-VQA using LoRA / QLoRA or run dry-run smoke tests.
Usage:
    python vqa_captioning/scripts/run_train.py --dry-run
    python vqa_captioning/scripts/run_train.py --config vqa_captioning/configs/qlora_qwen_3b.yaml
"""

import sys
import argparse
import yaml
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from vqa_captioning.training.train_vqa import VQATrainer

def main():
    parser = argparse.ArgumentParser(description="Train or smoke-test SatQuery-VQA.")
    parser.add_argument("--config", type=str, default="vqa_captioning/configs/base_config.yaml", help="Path to training config YAML")
    parser.add_argument("--dry-run", action="store_true", help="Run rapid smoke test on 10 samples without downloading full weights")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint directory to resume from")

    args = parser.parse_args()

    config_path = Path(args.config)
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    trainer = VQATrainer(config)

    if args.dry_run:
        print("Starting SatQuery-VQA dry-run smoke test...")
        results = trainer.run_dry_run_smoke_test(num_samples=10)
        print(f"\nSmoke Test Result: {results['status']}")
        print(f"Initial Loss     : {results['initial_loss']:.4f}")
        print(f"Checkpoint Saved : {results['checkpoint_saved']}")
        print(f"Sample Answer    : {results['test_prediction']['answer']}")
    else:
        print(f"Starting SatQuery-VQA training using config: {config_path}")
        results = trainer.train(resume_checkpoint=args.resume)
        print("\nTraining Result:", results)

if __name__ == "__main__":
    main()
