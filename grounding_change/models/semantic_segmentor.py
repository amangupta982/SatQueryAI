"""
Semantic Land-Cover Segmentation Head.
Predicts per-pixel semantic class probabilities for T1 and T2 independently,
enabling fine-grained land-cover classification and transition analysis.
"""

from typing import List, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


class SemanticSegmentationHead(nn.Module):
    """
    Predicts multi-class semantic land-cover maps for individual temporal scenes.
    """

    def __init__(self, in_dim: int = 256, num_classes: int = 7):
        super().__init__()
        self.num_classes = num_classes
        self.decoder = nn.Sequential(
            nn.Conv2d(in_dim, in_dim // 2, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(in_dim // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_dim // 2, in_dim // 4, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(in_dim // 4),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_dim // 4, num_classes, kernel_size=1)
        )

    def forward(self, feature_map: torch.Tensor, target_size: Tuple[int, int]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        feature_map: (B, C, H_feat, W_feat) from encoder (e.g. C2 or fused)
        target_size: (H, W)
        Returns:
            logits: (B, num_classes, H, W)
            probs: (B, num_classes, H, W) via softmax
        """
        up = F.interpolate(feature_map, size=target_size, mode="bilinear", align_corners=False)
        logits = self.decoder(up)
        probs = F.softmax(logits, dim=1)
        return logits, probs
