"""
Multi-Task Masked Loss Functions.
Implements:
  L_total = λ1*L_change + λ2*L_semantic + λ3*L_transition + λ4*L_grounding + λ5*L_vqa
Supports partial supervision via masked losses, ensuring samples are never
penalized for unavailable annotations.
"""

from typing import Any, Dict, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    """Smooth Dice loss for binary or multi-class masks."""

    def __init__(self, smooth: float = 1e-5):
        super().__init__()
        self.smooth = smooth

    def forward(self, pred_probs: torch.Tensor, target_masks: torch.Tensor) -> torch.Tensor:
        """
        pred_probs: (B, 1, H, W) or (B, H, W)
        target_masks: (B, 1, H, W) or (B, H, W) with values 0 or 1
        """
        p = pred_probs.view(-1)
        t = target_masks.view(-1).float()
        intersection = (p * t).sum()
        dice = (2.0 * intersection + self.smooth) / (p.sum() + t.sum() + self.smooth)
        return 1.0 - dice


class MultiTaskMaskedLoss(nn.Module):
    """
    Computes masked multi-task losses. If a batch element lacks a specific annotation,
    that element is masked out with zero loss contribution.
    """

    def __init__(
        self,
        lambda_change: float = 1.0,
        lambda_semantic: float = 0.8,
        lambda_transition: float = 0.6,
        lambda_grounding: float = 0.8,
        lambda_vqa: float = 0.5,
    ):
        super().__init__()
        self.lambda_change = lambda_change
        self.lambda_semantic = lambda_semantic
        self.lambda_transition = lambda_transition
        self.lambda_grounding = lambda_grounding
        self.lambda_vqa = lambda_vqa

        self.bce = nn.BCEWithLogitsLoss(reduction="none")
        self.ce = nn.CrossEntropyLoss(reduction="none", ignore_index=0)
        self.dice = DiceLoss()

    def forward(
        self,
        predictions: Dict[str, Any],
        targets: Dict[str, Any]
    ) -> Dict[str, torch.Tensor]:
        device = next(p.device for p in predictions.values() if isinstance(p, torch.Tensor))
        losses: Dict[str, torch.Tensor] = {
            "loss_change": torch.tensor(0.0, device=device),
            "loss_semantic": torch.tensor(0.0, device=device),
            "loss_transition": torch.tensor(0.0, device=device),
            "loss_grounding": torch.tensor(0.0, device=device),
            "loss_vqa": torch.tensor(0.0, device=device),
        }

        # 1. Binary Change Loss (BCE + Dice)
        if "change_mask" in targets and "change_logits" in predictions:
            mask_valid = targets.get("has_change_mask", torch.ones(len(targets["change_mask"]), dtype=torch.bool, device=device))
            if mask_valid.any():
                c_logits = predictions["change_logits"][mask_valid]
                c_target = targets["change_mask"][mask_valid].unsqueeze(1).float()
                bce_loss = self.bce(c_logits, c_target).mean()
                dice_loss = self.dice(torch.sigmoid(c_logits), c_target)
                losses["loss_change"] = bce_loss + dice_loss

        # 2. Semantic Segmentation Loss (CrossEntropy for T1 & T2)
        if "semantic_mask_t1" in targets and "sem_logits_t1" in predictions:
            mask_valid = targets.get("has_semantic_mask", torch.ones(len(targets["semantic_mask_t1"]), dtype=torch.bool, device=device))
            if mask_valid.any():
                s_logits_t1 = predictions["sem_logits_t1"][mask_valid]
                s_logits_t2 = predictions["sem_logits_t2"][mask_valid]
                s_target_t1 = targets["semantic_mask_t1"][mask_valid]
                s_target_t2 = targets["semantic_mask_t2"][mask_valid]
                loss_sem1 = self.ce(s_logits_t1, s_target_t1).mean()
                loss_sem2 = self.ce(s_logits_t2, s_target_t2).mean()
                losses["loss_semantic"] = 0.5 * (loss_sem1 + loss_sem2)

        # 3. Transition Loss
        if "transition_mask" in targets and "trans_logits" in predictions:
            mask_valid = targets.get("has_transition_mask", torch.ones(len(targets["transition_mask"]), dtype=torch.bool, device=device))
            if mask_valid.any():
                tr_logits = predictions["trans_logits"][mask_valid]
                tr_target = targets["transition_mask"][mask_valid]
                losses["loss_transition"] = self.ce(tr_logits, tr_target).mean()

        # 4. Visual Grounding Loss
        if "grounding_mask" in targets and "ground_logits" in predictions:
            mask_valid = targets.get("has_grounding_mask", torch.ones(len(targets["grounding_mask"]), dtype=torch.bool, device=device))
            if mask_valid.any():
                g_logits = predictions["ground_logits"][mask_valid]
                g_target = targets["grounding_mask"][mask_valid].unsqueeze(1).float()
                bce_g = self.bce(g_logits, g_target).mean()
                dice_g = self.dice(torch.sigmoid(g_logits), g_target)
                losses["loss_grounding"] = bce_g + dice_g

        # 5. VQA Loss
        if "vqa_label" in targets and "vqa_logits" in predictions:
            mask_valid = targets.get("has_vqa_label", torch.ones(len(targets["vqa_label"]), dtype=torch.bool, device=device))
            if mask_valid.any():
                v_logits = predictions["vqa_logits"][mask_valid]
                v_target = targets["vqa_label"][mask_valid]
                losses["loss_vqa"] = F.cross_entropy(v_logits, v_target).mean()

        # Weighted Total Multi-Task Loss
        total_loss = (
            self.lambda_change * losses["loss_change"]
            + self.lambda_semantic * losses["loss_semantic"]
            + self.lambda_transition * losses["loss_transition"]
            + self.lambda_grounding * losses["loss_grounding"]
            + self.lambda_vqa * losses["loss_vqa"]
        )
        losses["loss_total"] = total_loss
        return losses
