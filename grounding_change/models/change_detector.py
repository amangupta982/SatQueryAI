"""
Binary Change Segmentation Head.
FPN-style decoder taking fused temporal features and producing
continuous change intensity maps and binary change segmentation.
"""

from typing import List, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


class BinaryChangeHead(nn.Module):
    """
    Decoder that aggregates multi-scale temporal difference features (1/4 to 1/32)
    and predicts per-pixel binary change probabilities.
    """

    def __init__(self, feature_dim: int = 256, num_levels: int = 4):
        super().__init__()
        self.feature_dim = feature_dim

        # Lateral 1x1 convolutions
        self.laterals = nn.ModuleList([
            nn.Conv2d(feature_dim, feature_dim, kernel_size=1)
            for _ in range(num_levels)
        ])

        # Smooth 3x3 convolutions
        self.smooths = nn.ModuleList([
            nn.Conv2d(feature_dim, feature_dim, kernel_size=3, padding=1)
            for _ in range(num_levels)
        ])

        # Final prediction head
        self.head = nn.Sequential(
            nn.Conv2d(feature_dim, feature_dim // 2, kernel_size=3, padding=1),
            nn.BatchNorm2d(feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(feature_dim // 2, 1, kernel_size=1)
        )

    def forward(self, fused_features: List[torch.Tensor], target_size: Tuple[int, int]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        fused_features: [P2 (1/4), P3 (1/8), P4 (1/16), P5 (1/32)]
        target_size: (H, W) of original image
        Returns:
            logits: (B, 1, H, W)
            prob: (B, 1, H, W) in [0, 1]
        """
        # Top-down FPN aggregation
        p = self.laterals[-1](fused_features[-1])
        fpn_features = [self.smooths[-1](p)]

        for i in range(len(fused_features) - 2, -1, -1):
            lat = self.laterals[i](fused_features[i])
            p = lat + F.interpolate(p, size=lat.shape[-2:], mode="bilinear", align_corners=False)
            fpn_features.insert(0, self.smooths[i](p))

        # Upsample finest level (1/4) to target size and predict
        p2 = fpn_features[0]
        p_up = F.interpolate(p2, size=target_size, mode="bilinear", align_corners=False)
        logits = self.head(p_up)
        prob = torch.sigmoid(logits)

        return logits, prob
