"""
Temporal Fusion & Difference Representation Module.
Calculates Fdiff (directional change), Fabs (magnitude), and Fcat (joint representation),
fusing them through cross-temporal attention.
"""

from typing import List
import torch
import torch.nn as nn
import torch.nn.functional as F


class TemporalDifferenceBlock(nn.Module):
    """
    Computes directional difference (F2 - F1), absolute magnitude (|F2 - F1|),
    and concatenated features (concat(F1, F2)), projecting them to a unified feature dim.
    """

    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        # in_dim * 4 because: F1 (in_dim) + F2 (in_dim) + Fdiff (in_dim) + Fabs (in_dim) = in_dim * 4
        self.fusion_conv = nn.Sequential(
            nn.Conv2d(in_dim * 4, out_dim, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_dim),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_dim, out_dim, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_dim),
            nn.ReLU(inplace=True),
        )

        # Channel attention gate
        self.ca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(out_dim, out_dim // 4, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_dim // 4, out_dim, kernel_size=1),
            nn.Sigmoid()
        )

    def forward(self, f1: torch.Tensor, f2: torch.Tensor) -> torch.Tensor:
        fdiff = f2 - f1
        fabs = torch.abs(f2 - f1)
        fcat = torch.cat([f1, f2], dim=1)

        f_all = torch.cat([fcat, fdiff, fabs], dim=1)
        fused = self.fusion_conv(f_all)
        att = self.ca(fused)
        return fused * att


class TemporalFusionModule(nn.Module):
    """
    Multi-scale temporal fusion across all backbone stages (C2 to C5).
    Fuses each level and unifies them into a shared feature dimension.
    """

    def __init__(self, in_channels: List[int], feature_dim: int = 256):
        super().__init__()
        self.blocks = nn.ModuleList([
            TemporalDifferenceBlock(in_dim, feature_dim)
            for in_dim in in_channels
        ])
        self.feature_dim = feature_dim

    def forward(self, f1_levels: List[torch.Tensor], f2_levels: List[torch.Tensor]) -> List[torch.Tensor]:
        fused_levels = []
        for block, f1, f2 in zip(self.blocks, f1_levels, f2_levels):
            fused_levels.append(block(f1, f2))
        return fused_levels
