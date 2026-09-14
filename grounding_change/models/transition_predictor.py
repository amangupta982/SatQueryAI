"""
Semantic Transition Prediction Head.
Directly models before->after land-cover transitions (e.g. vegetation -> building).
"""

from typing import Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


class TransitionPredictionHead(nn.Module):
    """
    Predicts land-cover transition probabilities given fused temporal difference representations.
    Can model num_classes x num_classes transitions.
    """

    def __init__(self, in_dim: int = 256, num_classes: int = 7):
        super().__init__()
        self.num_classes = num_classes
        self.total_transitions = num_classes * num_classes

        self.head = nn.Sequential(
            nn.Conv2d(in_dim, in_dim // 2, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(in_dim // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_dim // 2, self.total_transitions, kernel_size=1)
        )

    def forward(self, fused_feat: torch.Tensor, target_size: Tuple[int, int]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        fused_feat: (B, C, H_feat, W_feat)
        target_size: (H, W)
        Returns:
            logits: (B, num_classes*num_classes, H, W)
            probs: (B, num_classes*num_classes, H, W)
        """
        up = F.interpolate(fused_feat, size=target_size, mode="bilinear", align_corners=False)
        logits = self.head(up)
        probs = F.softmax(logits, dim=1)
        return logits, probs

    def decode_transition_index(self, index: int) -> Tuple[int, int]:
        """Convert linear transition index back to (from_class_id, to_class_id)."""
        from_cls = index // self.num_classes
        to_cls = index % self.num_classes
        return from_cls, to_cls
