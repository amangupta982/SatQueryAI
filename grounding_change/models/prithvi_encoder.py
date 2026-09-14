"""
Prithvi-EO-2.0 Foundation Optical Encoder
Paper: "Prithvi-EO-2.0: A Versatile Multi-Temporal Foundation Model for Earth Observation Applications"
arXiv: https://arxiv.org/abs/2412.02732
Hugging Face: ibm-nasa-geospatial/Prithvi-EO-2.0-300M

Implements the optical branch foundation encoder accepting Sentinel-2 multispectral
bands (B02, B03, B04, B8A, B11, B12) or standard RGB, producing hierarchical multi-scale
visual embeddings.
"""

import math
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from grounding_change.config import settings

logger = logging.getLogger("PrithviOpticalEncoder")

# Official HLS Per-Band Normalization Parameters (B02, B03, B04, B8A, B11, B12)
HLS_BAND_MEANS = [1087.0, 1342.0, 1433.0, 2734.0, 1958.0, 1363.0]
HLS_BAND_STDS = [2248.0, 2179.0, 2178.0, 1850.0, 1242.0, 1049.0]


class PatchEmbed3D(nn.Module):
    """
    3D spatiotemporal patch embedding layer compatible with Prithvi-EO-2.0 ViT.
    Projects multi-band optical patches (B, C, H, W) to transformer tokens (B, N, D).
    """

    def __init__(
        self,
        img_size: int = 224,
        patch_size: int = 16,
        in_chans: int = 6,
        embed_dim: int = 1024,
    ):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.grid_size = img_size // patch_size
        self.num_patches = self.grid_size * self.grid_size

        # Convolutional patch projection
        self.proj = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, H, W)
        B, C, H, W = x.shape
        x = self.proj(x)  # (B, D, H/p, W/p)
        x = x.flatten(2).transpose(1, 2)  # (B, N, D)
        x = self.norm(x)
        return x


class TransformerBlock(nn.Module):
    """Multi-Head Self-Attention block for Prithvi ViT."""

    def __init__(self, embed_dim: int = 1024, num_heads: int = 16, mlp_ratio: float = 4.0, dropout: float = 0.1):
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
        # Self-attention with residual connection
        normed = self.norm1(x)
        attn_out, _ = self.attn(normed, normed, normed)
        x = x + attn_out
        # MLP with residual connection
        x = x + self.mlp(self.norm2(x))
        return x


class PrithviEO2OpticalEncoder(nn.Module):
    """
    Prithvi-EO-2.0-300M Optical Foundation Encoder.
    Ingests multi-band Sentinel-2 imagery and produces multi-scale spatial feature maps
    (P2, P3, P4, P5) projected to unified feature_dim.
    """

    def __init__(
        self,
        in_channels: int = 6,
        embed_dim: int = 1024,
        depth: int = 6,  # Scaled block depth for fast local inference
        num_heads: int = 16,
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

        # Adaptive channel adapter to handle variable inputs (RGB 3-ch, RGB-NIR 4-ch, or full 6-ch)
        self.channel_adapter = nn.Sequential(
            nn.Conv2d(in_channels, 6, kernel_size=1),
            nn.BatchNorm2d(6),
            nn.ReLU(inplace=True)
        ) if in_channels != 6 else nn.Identity()

        # Patch Embedding
        self.patch_embed = PatchEmbed3D(
            img_size=img_size,
            patch_size=patch_size,
            in_chans=6,
            embed_dim=embed_dim
        )

        # Positional Embeddings
        num_patches = self.patch_embed.num_patches
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, embed_dim))
        nn.init.trunc_normal_(self.pos_embed, std=0.02)

        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim=embed_dim, num_heads=num_heads, dropout=0.1)
            for _ in range(depth)
        ])
        self.norm = nn.LayerNorm(embed_dim)

        # Multi-scale FPN-style projection heads to match downstream decoders
        # Projects ViT spatial tokens (H/16, W/16) to scales 1/4, 1/8, 1/16, 1/32
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
        """Load pretrained Prithvi-EO-2.0 state dictionary with non-strict mapping."""
        logger.info(f"Loading Prithvi-EO-2.0 weights from {path}")
        try:
            state_dict = torch.load(path, map_location="cpu")
            self.load_state_dict(state_dict, strict=False)
            logger.info("Successfully loaded optical backbone weights.")
        except Exception as e:
            logger.warning(f"Could not load Prithvi weights from {path}: {e}")

    def normalize_hls(self, x: torch.Tensor) -> torch.Tensor:
        """Apply official HLS reflectance per-band mean and std normalization."""
        if x.shape[1] == 6:
            means = torch.tensor(HLS_BAND_MEANS, device=x.device).view(1, 6, 1, 1)
            stds = torch.tensor(HLS_BAND_STDS, device=x.device).view(1, 6, 1, 1)
            return (x - means) / (stds + 1e-6)
        return x

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass for Optical Foundation Encoder.
        x: (B, C, H, W) where C is 3 (RGB), 4 (RGB-NIR), or 6 (HLS/Sentinel-2)
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

        # Resize to internal img_size if necessary
        if H != self.img_size or W != self.img_size:
            x = F.interpolate(x, size=(self.img_size, self.img_size), mode="bilinear", align_corners=False)

        # Channel adaptation (if RGB, projects 3 -> 6 bands)
        x = self.channel_adapter(x)

        # Patch embedding -> (B, N, D)
        tokens = self.patch_embed(x)
        tokens = tokens + self.pos_embed

        # Transformer blocks
        for block in self.blocks:
            tokens = block(tokens)
        tokens = self.norm(tokens)

        # Reshape tokens to 2D spatial grid (B, D, H/16, W/16)
        grid_size = self.patch_embed.grid_size
        feat_2d = tokens.transpose(1, 2).reshape(B, self.embed_dim, grid_size, grid_size)

        # Multiscale feature pyramid projections
        p2 = self.fpn_p2(feat_2d)
        p3 = self.fpn_p3(feat_2d)
        p4 = self.fpn_p4(feat_2d)
        p5 = self.fpn_p5(feat_2d)

        # Global pooled visual embedding
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
