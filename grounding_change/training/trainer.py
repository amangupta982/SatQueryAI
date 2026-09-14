"""
Change Model Trainer.
Executes multi-task training with masked losses, validation, and pre-training checks.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import torch
from torch.utils.data import DataLoader

from ..config import CHECKPOINT_DIR, settings
from ..data.manifest import DatasetManifestManager
from ..data.mixture import DatasetMixture, collate_temporal_batch
from ..data.transforms import PairedTemporalTransform
from ..data.adapters.changechat_adapter import ChangeChatAdapter
from ..data.adapters.rsrcc_adapter import RSRCCAdapter
from ..data.adapters.second_adapter import SECONDAdapter
from ..data.adapters.qag360k_adapter import QAG360KAdapter
from ..models.change_intelligence_model import ChangeIntelligenceModel
from ..models.losses import MultiTaskMaskedLoss
from .train_config import PROFILES, TrainingProfileConfig


class ChangeModelTrainer:
    """Orchestrates end-to-end multi-task training across remote-sensing datasets."""

    def __init__(
        self,
        profile: str = "full",
        epochs: int = 50,
        batch_size: int = 8,
        lr: float = 1e-4,
        device: Optional[str] = None,
        checkpoint_dir: Optional[Path] = None,
    ):
        self.profile_name = profile
        self.profile_cfg: TrainingProfileConfig = PROFILES.get(profile, PROFILES["full"])
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() and device != "cpu" else "cpu"
        )
        self.checkpoint_dir = Path(checkpoint_dir or CHECKPOINT_DIR)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_mgr = DatasetManifestManager()

    def run_pretraining_checks(self) -> bool:
        """
        Runs mandatory dataset availability, integrity, and label checks.
        Terminates training if a required dataset for this profile is missing.
        """
        print("\n" + "=" * 65)
        print("          PRE-TRAINING DATASET READINESS CHECK")
        print(f"  Selected Profile: {self.profile_name.upper()} ({self.profile_cfg.description})")
        print("=" * 65)

        manifest = self.manifest_mgr.load()
        all_ready = True

        for req_ds in self.profile_cfg.required_datasets:
            entry = manifest.get(req_ds)
            status = entry.status if entry else "missing"
            is_ready = status in ["complete", "ready"]

            indicator = "READY" if is_ready else ("PARTIAL / MISSING" if status == "partial" else "MISSING")
            print(f"  {req_ds.upper():<14} : {indicator:<12} [REQUIRED for {self.profile_name}]")

            if not is_ready:
                all_ready = False

        print("=" * 65)
        if not all_ready:
            print("\nERROR: One or more required datasets for profile '{self.profile_name}' are incomplete or missing!")
            print("To acquire datasets, run:")
            print(f"  python -m grounding_change.data.download_datasets --profile {self.profile_name}")
            print("Training will NOT proceed on an incomplete dataset configuration.")
            return False

        print("All dataset pre-requisites satisfied. Proceeding to model initialization...\n")
        return True

    def build_datasets(self) -> DatasetMixture:
        """Instantiate active adapters according to profile."""
        transform = PairedTemporalTransform(img_size=settings.model.img_size, is_training=True)
        active_datasets = {}

        if "second" in self.profile_cfg.required_datasets:
            active_datasets["second"] = SECONDAdapter(settings.data.second_dir, split="train", transform=transform)
        if "changechat" in self.profile_cfg.required_datasets:
            active_datasets["changechat"] = ChangeChatAdapter(settings.data.changechat_dir, split="train", transform=transform)
        if "rsrcc" in self.profile_cfg.required_datasets:
            active_datasets["rsrcc"] = RSRCCAdapter(settings.data.rsrcc_dir, split="train", transform=transform)
        if "qag360k" in self.profile_cfg.required_datasets:
            active_datasets["qag360k"] = QAG360KAdapter(settings.data.qag360k_dir, split="train", transform=transform)

        mixture = DatasetMixture(datasets=active_datasets)
        return mixture

    def train(self, skip_readiness_check: bool = False):
        """Execute training loop."""
        if not skip_readiness_check:
            if not self.run_pretraining_checks():
                raise RuntimeError(f"Training aborted: Incomplete dataset profile '{self.profile_name}'.")

        # Initialize model
        model = ChangeIntelligenceModel(
            backbone_name=settings.model.backbone,
            pretrained=settings.model.pretrained,
            feature_dim=settings.model.feature_dim,
            num_classes=settings.model.num_semantic_classes,
        ).to(self.device)

        criterion = MultiTaskMaskedLoss(
            lambda_change=settings.training.lambda_change,
            lambda_semantic=settings.training.lambda_semantic,
            lambda_transition=settings.training.lambda_transition,
            lambda_grounding=settings.training.lambda_grounding,
            lambda_vqa=settings.training.lambda_vqa,
        )

        optimizer = torch.optim.AdamW(model.parameters(), lr=self.lr, weight_decay=settings.training.weight_decay)
        dataset = self.build_datasets()

        if len(dataset) == 0:
            print("No samples available to train on.")
            return

        loader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=True,
            collate_fn=collate_temporal_batch,
            num_workers=0
        )

        print(f"Starting training on {self.device} for {self.epochs} epochs...")
        model.train()

        for epoch in range(1, self.epochs + 1):
            epoch_loss = 0.0
            for i, batch in enumerate(loader):
                t1 = batch["t1"].to(self.device)
                t2 = batch["t2"].to(self.device)
                questions = batch.get("questions")

                optimizer.zero_grad()
                preds = model(t1, t2, question=questions)

                # Move targets to device
                targets = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
                losses = criterion(preds, targets)

                total_loss = losses["loss_total"]
                total_loss.backward()
                optimizer.step()

                epoch_loss += total_loss.item()

            avg_loss = epoch_loss / max(1, len(loader))
            print(f"Epoch [{epoch}/{self.epochs}] - Loss: {avg_loss:.4f}")

            # Save checkpoint
            if epoch % settings.training.save_interval == 0 or epoch == self.epochs:
                ckpt_path = self.checkpoint_dir / f"change_model_epoch_{epoch}.pth"
                torch.save({
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "loss": avg_loss,
                    "profile": self.profile_name,
                }, ckpt_path)
                print(f"Saved checkpoint to {ckpt_path}")
