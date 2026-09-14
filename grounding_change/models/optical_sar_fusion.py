"""
Optical-SAR Cross-Modal Alignment and Cross-Attention Fusion Module
Enables bidirectional information exchange between optical multispectral
representations and radar backscatter representations while preserving
modality-specific, cross-attended, and fused feature representations.
"""

import math
import logging
from typing import Any, Dict, List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F

from grounding_change.config import settings

logger = logging.getLogger("OpticalSARFusion")


class CrossAttentionLayer(nn.Module):
    """
    Bidirectional Cross-Attention module between Optical and SAR token streams.
    Q_opt attends to K_sar, V_sar, and Q_sar attends to K_opt, V_opt.
    """

    def __init__(self, embed_dim: int = 256, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads

        # Optical -> SAR attention
        self.attn_opt_to_sar = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout, batch_first=True)
        self.norm_opt = nn.LayerNorm(embed_dim)

        # SAR -> Optical attention
        self.attn_sar_to_opt = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout, batch_first=True)
        self.norm_sar = nn.LayerNorm(embed_dim)

        # Gated feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim * 4, embed_dim),
            nn.Dropout(dropout)
        )
        self.norm_fused = nn.LayerNorm(embed_dim)

    def forward(self, f_opt: torch.Tensor, f_sar: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        f_opt: (B, N, D)
        f_sar: (B, N, D)
        Returns:
            f_opt_cross: Optical tokens enriched with SAR radar scattering context
            f_sar_cross: SAR tokens enriched with Optical spectral reflectance context
            f_fused: Joint multimodal token representation
        """
        # Optical queries SAR
        opt_attended, _ = self.attn_opt_to_sar(query=f_opt, key=f_sar, value=f_sar)
        f_opt_cross = self.norm_opt(f_opt + opt_attended)

        # SAR queries Optical
        sar_attended, _ = self.attn_sar_to_opt(query=f_sar, key=f_opt, value=f_opt)
        f_sar_cross = self.norm_sar(f_sar + sar_attended)

        # Fused representation via gated FFN
        cat_tokens = torch.cat([f_opt_cross, f_sar_cross], dim=-1)
        f_fused = self.norm_fused(f_opt_cross + f_sar_cross + self.ffn(cat_tokens))

        return f_opt_cross, f_sar_cross, f_fused


class OpticalSARFusionModule(nn.Module):
    """
    Master Multimodal Alignment & Fusion Module.
    Preserves:
      1. F_opt: Pure Optical Representations
      2. F_sar: Pure SAR Representations
      3. F_cross: Cross-attended representations
      4. F_fused: Fused joint multimodal representation
    Also computes cross-modal difference metrics between co-registered pairs.
    """

    def __init__(
        self,
        feature_dim: int = 256,
        num_heads: int = 8,
        dropout: float = 0.1
    ):
        super().__init__()
        self.feature_dim = feature_dim

        # Multiscale spatial cross-attention layers across pyramid levels
        self.cross_attn_p2 = CrossAttentionLayer(embed_dim=feature_dim, num_heads=num_heads, dropout=dropout)
        self.cross_attn_p3 = CrossAttentionLayer(embed_dim=feature_dim, num_heads=num_heads, dropout=dropout)
        self.cross_attn_p4 = CrossAttentionLayer(embed_dim=feature_dim, num_heads=num_heads, dropout=dropout)
        self.cross_attn_p5 = CrossAttentionLayer(embed_dim=feature_dim, num_heads=num_heads, dropout=dropout)

        # Global vector cross-attention
        self.global_cross_attn = CrossAttentionLayer(embed_dim=feature_dim, num_heads=num_heads, dropout=dropout)
        self.proj_opt_global = nn.Linear(1024, feature_dim)
        self.proj_sar_global = nn.Linear(768, feature_dim)

        # Cross-modal difference head: computes sensor complementarity map
        self.diff_conv = nn.Sequential(
            nn.Conv2d(feature_dim * 2, feature_dim, kernel_size=3, padding=1),
            nn.BatchNorm2d(feature_dim),
            nn.ReLU(inplace=True),
            nn.Conv2d(feature_dim, 1, kernel_size=1),
            nn.Sigmoid()
        )

    def _apply_level_fusion(
        self,
        opt_level: torch.Tensor,
        sar_level: torch.Tensor,
        cross_attn_module: CrossAttentionLayer
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Flatten 2D feature map, run cross-attention, reshape back to (B, C, H, W)."""
        B, C, H, W = opt_level.shape
        # (B, N, C) where N = H * W
        opt_tokens = opt_level.flatten(2).transpose(1, 2)
        sar_tokens = sar_level.flatten(2).transpose(1, 2)

        opt_cross, sar_cross, fused = cross_attn_module(opt_tokens, sar_tokens)

        opt_cross_2d = opt_cross.transpose(1, 2).reshape(B, C, H, W)
        sar_cross_2d = sar_cross.transpose(1, 2).reshape(B, C, H, W)
        fused_2d = fused.transpose(1, 2).reshape(B, C, H, W)

        return opt_cross_2d, sar_cross_2d, fused_2d

    def forward(
        self,
        optical_features: Dict[str, torch.Tensor],
        sar_features: Dict[str, torch.Tensor]
    ) -> Dict[str, Any]:
        """
        optical_features: Dict from PrithviEO2OpticalEncoder containing p2, p3, p4, p5, global_feature
        sar_features: Dict from SummitSAREncoder containing p2, p3, p4, p5, global_feature
        """
        # 1. Level P2 (1/4 scale)
        p2_opt_cross, p2_sar_cross, p2_fused = self._apply_level_fusion(
            optical_features["p2"], sar_features["p2"], self.cross_attn_p2
        )

        # 2. Level P3 (1/8 scale)
        p3_opt_cross, p3_sar_cross, p3_fused = self._apply_level_fusion(
            optical_features["p3"], sar_features["p3"], self.cross_attn_p3
        )

        # 3. Level P4 (1/16 scale)
        p4_opt_cross, p4_sar_cross, p4_fused = self._apply_level_fusion(
            optical_features["p4"], sar_features["p4"], self.cross_attn_p4
        )

        # 4. Level P5 (1/32 scale)
        p5_opt_cross, p5_sar_cross, p5_fused = self._apply_level_fusion(
            optical_features["p5"], sar_features["p5"], self.cross_attn_p5
        )

        # 5. Global representation fusion
        opt_glob = self.proj_opt_global(optical_features["global_feature"]).unsqueeze(1)  # (B, 1, D)
        sar_glob = self.proj_sar_global(sar_features["global_feature"]).unsqueeze(1)      # (B, 1, D)
        _, _, fused_global = self.global_cross_attn(opt_glob, sar_glob)
        fused_global = fused_global.squeeze(1)  # (B, D)

        # 6. Compute Cross-Modal Difference Map on P2 (1/4 scale)
        diff_input = torch.cat([optical_features["p2"], sar_features["p2"]], dim=1)
        cross_modal_diff_map = self.diff_conv(diff_input)  # (B, 1, H/4, W/4)

        return {
            # Preserved Optical-specific
            "F_opt": optical_features,
            # Preserved SAR-specific
            "F_sar": sar_features,
            # Cross-attended representations
            "F_cross": {
                "opt_cross": {"p2": p2_opt_cross, "p3": p3_opt_cross, "p4": p4_opt_cross, "p5": p5_opt_cross},
                "sar_cross": {"p2": p2_sar_cross, "p3": p3_sar_cross, "p4": p4_sar_cross, "p5": p5_sar_cross},
            },
            # Unified Multimodal fused representation
            "F_fused": {
                "p2": p2_fused,
                "p3": p3_fused,
                "p4": p4_fused,
                "p5": p5_fused,
                "global_feature": fused_global
            },
            # Cross-modal complementarity difference map
            "cross_modal_diff_map": cross_modal_diff_map
        }
