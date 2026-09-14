"""
CLI entry point for training grounding_change models.

Usage:
  python -m grounding_change.training.train --profile minimal --epochs 10
  python -m grounding_change.training.train --profile full --epochs 50 --batch-size 8
"""

import argparse
import sys
from .trainer import ChangeModelTrainer
from .train_config import PROFILES


def main():
    parser = argparse.ArgumentParser(description="SatQueryAI Change Intelligence Training Pipeline")
    parser.add_argument("--profile", choices=list(PROFILES.keys()), default="full", help="Training profile")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto", help="Compute device")
    parser.add_argument("--skip-check", action="store_true", help="Skip dataset pre-check (development only)")

    args = parser.parse_args()

    trainer = ChangeModelTrainer(
        profile=args.profile,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=args.device
    )

    try:
        trainer.train(skip_readiness_check=args.skip_check)
    except RuntimeError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
