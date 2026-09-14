"""
SUMMIT SAR Foundation Encoder
Paper: "SUMMIT: SAR Foundational Model with Multiple Auxiliary Tasks Enhanced Intrinsic Characteristics"
Target Sensor: Sentinel-1 Dual-Polarization SAR (VV, VH Ground Range Detected)

Implements the SAR branch foundation encoder specifically designed around radar backscatter
scattering physics, speckle invariance, and structural dielectric features.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("SummitSAREncoder")


class SARScatteringEnhancementBlock(nn.Module):
    """
    Radar physical scattering enhancement module.
    Models double-bounce (urban/structures), volume scattering (vegetation),
    and surface scattering (water/smooth ground) from VV and VH polarizations.
    """

    def __init__(self, in_channels: int = 2, out_channels: int = 64):
        super().__init__()
        # Extract direct intensity and dual-polarization cross-ratio (VH/VV)
        self.conv_spatial = nn.Sequential(
            nn.Conv2d(in_channels, out_channels // 2, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels // 2),
            nn.GELU()
        )
        self.conv_ratio = nn.Sequential(
            nn.Conv2d(in_channels, out_channels // 2, kernel_size=1),
            nn.BatchNorm2d(out_channels // 2),
            nn.GELU()
        )
        self.fuse = nn.Sequential(
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.GELU()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, 2, H, W) [VV, VH]
        f_spatial = self.conv_spatial(x)
        # Compute polarization difference / ratio features
        diff = torch.abs(x[:, 0:1] - x[:, 1:2])
        sum_pol = x[:, 0:1] + x[:, 1:2] + 1e-6
        pol_ratio = diff / sum_pol
        pol_stack = torch.cat([pol_ratio, x[:, 1:2]], dim=1)
        f_ratio = self.conv_ratio(pol_stack)

        out = self.fuse(torch.cat([f_spatial, f_ratio], dim=1))
        return out


class SARTransformerBlock(nn.Module):
    """Speckle-invariant self-attention block for SAR features."""

    def __init__(self, embed_dim: int = 768, num_heads: int = 12, mlp_ratio: float = 4.0, dropout: float = 0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout, batch_first=True)
        self.norm2 = nn.LayerNorm(embed_dim)
        mlp_hidden_dim = int(embed_dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, mlp_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden_dim, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        normed = self.norm1(x)
        attn_out, _ = self.attn(normed, normed, normed)
        x = x + attn_out
        x = x + self.mlp(self.norm2(x))
        return x


class SummitSAREncoder(nn.Module):
    """
    SUMMIT SAR Foundation Encoder.
    Processes Sentinel-1 dual-pol (VV, VH) backscatter imagery into rich multi-scale
    structural and dielectric representations.
    """

    def __init__(
        self,
        in_channels: int = 2,
        embed_dim: int = 768,
        depth: int = 6,
        num_heads: int = 12,
        feature_dim: int = 256,
        img_size: int = 224,
        patch_size: int = 16,
        pretrained_weights_path: Optional[str] = None,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.embed_dim = embed_dim
        self.feature_dim = feature_dim
        self.img_size = img_size
        self.patch_size = patch_size

        # Scattering physics front-end
        self.scattering_frontend = SARScatteringEnhancementBlock(in_channels=in_channels, out_channels=64)

        # Patch embedding from scattering features
        self.patch_embed = nn.Conv2d(64, embed_dim, kernel_size=patch_size, stride=patch_size)
        self.norm = nn.LayerNorm(embed_dim)

        # Position embeddings
        grid_size = img_size // patch_size
        self.grid_size = grid_size
        self.num_patches = grid_size * grid_size
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches, embed_dim))
        nn.init.trunc_normal_(self.pos_embed, std=0.02)

        # Transformer blocks
        self.blocks = nn.ModuleList([
            SARTransformerBlock(embed_dim=embed_dim, num_heads=num_heads, dropout=0.1)
            for _ in range(depth)
        ])

        # Multi-scale FPN projection heads
        self.fpn_p2 = nn.Sequential(
            nn.ConvTranspose2d(embed_dim, feature_dim, kernel_size=4, stride=4),
            nn.BatchNorm2d(feature_dim),
            nn.ReLU(inplace=True)
        )
        self.fpn_p3 = nn.Sequential(
            nn.ConvTranspose2d(embed_dim, feature_dim, kernel_size=2, stride=2),
            nn.BatchNorm2d(feature_dim),
            nn.ReLU(inplace=True)
        )
        self.fpn_p4 = nn.Sequential(
            nn.Conv2d(embed_dim, feature_dim, kernel_size=1),
            nn.BatchNorm2d(feature_dim),
            nn.ReLU(inplace=True)
        )
        self.fpn_p5 = nn.Sequential(
            nn.Conv2d(embed_dim, feature_dim, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(feature_dim),
            nn.ReLU(inplace=True)
        )

        if pretrained_weights_path and Path(pretrained_weights_path).exists():
            self._load_pretrained(pretrained_weights_path)

    def _load_pretrained(self, path: str) -> None:
        """Load pretrained SAR foundation weights."""
        logger.info(f"Loading SAR foundation weights from {path}")
        try:
            state_dict = torch.load(path, map_location="cpu")
            self.load_state_dict(state_dict, strict=False)
            logger.info("Successfully loaded SAR backbone weights.")
        except Exception as e:
            logger.warning(f"Could not load SAR weights from {path}: {e}")

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass for SAR Foundation Encoder.
        x: (B, 2, H, W) [VV, VH amplitude or dB values]
        Returns:
            Dict containing multi-scale pyramid levels:
            'p2': (B, feature_dim, H/4, W/4)
            'p3': (B, feature_dim, H/8, W/8)
            'p4': (B, feature_dim, H/16, W/16)
            'p5': (B, feature_dim, H/32, W/32)
            'tokens': (B, N, embed_dim)
            'global_feature': (B, embed_dim)
        """
        B, C, H, W = x.shape

        if H != self.img_size or W != self.img_size:
            x = F.interpolate(x, size=(self.img_size, self.img_size), mode="bilinear", align_corners=False)

        # Scattering front-end
        scattering_feats = self.scattering_frontend(x)  # (B, 64, H, W)

        # Patch embedding
        tokens = self.patch_embed(scattering_feats)  # (B, D, H/p, W/p)
        tokens = tokens.flatten(2).transpose(1, 2)   # (B, N, D)
        tokens = tokens + self.pos_embed

        # Transformer blocks
        for block in self.blocks:
            tokens = block(tokens)
        tokens = self.norm(tokens)

        # Reshape tokens to 2D spatial grid (B, D, H/16, W/16)
        feat_2d = tokens.transpose(1, 2).reshape(B, self.embed_dim, self.grid_size, self.grid_size)

        # Multi-scale pyramid projections
        p2 = self.fpn_p2(feat_2d)
        p3 = self.fpn_p3(feat_2d)
        p4 = self.fpn_p4(feat_2d)
        p5 = self.fpn_p5(feat_2d)

        global_feature = tokens.mean(dim=1)

        return {
            "p2": p2,
            "p3": p3,
            "p4": p4,
            "p5": p5,
            "tokens": tokens,
            "global_feature": global_feature,
            "feat_2d": feat_2d
        }
