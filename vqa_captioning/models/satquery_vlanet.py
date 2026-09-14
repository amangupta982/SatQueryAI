"""
SatQueryVLANet: Authentic Remote-Sensing Vision-Language Architecture.
Processes Sentinel-2 / SAR satellite imagery and natural language questions
using a dual-stream Convolutional Vision Backbone + Text GRU Encoder + Cross-Attention Multimodal Fusion.
Trained on BigEarthNet.txt dataset splits.
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

logger = logging.getLogger(__name__)

# Canonical BigEarthNet-19 Land Cover Classes
CLC_19_CLASSES = [
    "Urban fabric",
    "Industrial or commercial units",
    "Arable land",
    "Permanent crops",
    "Pastures",
    "Complex cultivation patterns",
    "Land principally occupied by agriculture, with significant areas of natural vegetation",
    "Agro-forestry areas",
    "Broad-leaved forest",
    "Coniferous forest",
    "Mixed forest",
    "Natural grasslands and sclerophyllous vegetation",
    "Moors and heathland",
    "Transitional woodland, shrub",
    "Beaches, dunes, sands",
    "Inland wetlands",
    "Coastal wetlands",
    "Inland waters",
    "Marine waters",
]

class SatQuerySpectralExtractor:
    """Extracts calibrated spectral, texture, and color metrics from satellite imagery."""

    @staticmethod
    def extract_features(pil_image: Image.Image) -> Tuple[torch.Tensor, Dict[str, float]]:
        img_np = np.array(pil_image.convert("RGB"), dtype=np.float32) / 255.0
        h, w, c = img_np.shape

        r = img_np[:, :, 0]
        g = img_np[:, :, 1]
        b = img_np[:, :, 2]

        eps = 1e-6
        # Normalized Difference Greenness Index (NDGI / pseudo-NDVI in RGB)
        ndgi = (g - r) / (g + r + eps)
        # Normalized Difference Water Index (NDWI proxy in RGB: Blue-dominant vs Red)
        ndwi = (b - r) / (b + r + eps)
        # Brightness (Value)
        brightness = (r + g + b) / 3.0

        # Fractional coverage estimation
        veg_mask = (ndgi > 0.05) & (g > b)
        water_mask = (b > r * 1.1) & (b > g * 0.9) & (brightness < 0.45)
        urban_mask = (np.abs(r - g) < 0.08) & (np.abs(g - b) < 0.08) & (brightness > 0.25)
        agri_mask = (r > 0.3) & (g > 0.25) & (b < 0.3) & (~veg_mask)

        veg_pct = float(np.mean(veg_mask) * 100.0)
        water_pct = float(np.mean(water_mask) * 100.0)
        urban_pct = float(np.mean(urban_mask) * 100.0)
        agri_pct = float(np.mean(agri_mask) * 100.0)
        other_pct = max(0.0, 100.0 - (veg_pct + water_pct + urban_pct + agri_pct))

        # Spatial quadrant distribution for spatial relationship questions
        mid_h, mid_w = h // 2, w // 2
        top_veg = float(np.mean(veg_mask[:mid_h, :]))
        bottom_veg = float(np.mean(veg_mask[mid_h:, :]))
        left_veg = float(np.mean(veg_mask[:, :mid_w]))
        right_veg = float(np.mean(veg_mask[:, mid_w:]))

        top_water = float(np.mean(water_mask[:mid_h, :]))
        bottom_water = float(np.mean(water_mask[mid_h:, :]))
        left_water = float(np.mean(water_mask[:, :mid_w]))
        right_water = float(np.mean(water_mask[:, mid_w:]))

        feature_vector = torch.tensor([
            veg_pct / 100.0,
            water_pct / 100.0,
            urban_pct / 100.0,
            agri_pct / 100.0,
            float(np.mean(ndgi)),
            float(np.mean(brightness)),
            float(np.std(brightness)),
            top_water,
            bottom_water,
            left_water,
            right_water,
            top_veg,
            bottom_veg,
            left_veg,
            right_veg,
            float(np.mean(ndwi)),
        ], dtype=torch.float32)

        metrics = {
            "vegetation_percentage": round(veg_pct, 1),
            "water_percentage": round(water_pct, 1),
            "urban_percentage": round(urban_pct, 1),
            "agriculture_percentage": round(agri_pct, 1),
            "other_percentage": round(other_pct, 1),
            "mean_greenness_index": round(float(np.mean(ndgi)), 3),
            "mean_reflectance": round(float(np.mean(brightness)), 3),
        }

        return feature_vector, metrics


class SatQueryVLANet(nn.Module):
    """
    Multimodal Vision-Language Network for Remote Sensing VQA.
    """

    def __init__(
        self,
        vocab_size: int = 15000,
        embed_dim: int = 128,
        hidden_dim: int = 256,
        num_clc_classes: int = 19,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim

        # 1. Vision Convolutional Stream (Processes 120x120 satellite RGB)
        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),   # -> 60x60
            nn.BatchNorm2d(32),
            nn.GELU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),  # -> 30x30
            nn.BatchNorm2d(64),
            nn.GELU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1), # -> 15x15
            nn.BatchNorm2d(128),
            nn.GELU(),
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),# -> 8x8
            nn.BatchNorm2d(256),
            nn.GELU(),
            nn.AdaptiveAvgPool2d((4, 4)),                            # -> (B, 256, 4, 4)
        )
        # 16 spatial tokens of dimension 256 + 16 spectral features
        self.spatial_proj = nn.Linear(256, hidden_dim)
        self.spectral_proj = nn.Linear(16, hidden_dim)

        # 2. Text / Question Stream
        self.token_embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.text_gru = nn.GRU(
            embed_dim,
            hidden_dim // 2,
            batch_first=True,
            bidirectional=True,
        )

        # 3. Multimodal Cross-Attention
        self.cross_attn = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=4, batch_first=True)
        self.layer_norm = nn.LayerNorm(hidden_dim)

        # 4. Multimodal Fusion
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.Dropout(0.1),
        )

        # 5. Dedicated Task Prediction Heads
        self.mcq_head = nn.Linear(hidden_dim, 4)            # a, b, c, d
        self.binary_head = nn.Linear(hidden_dim, 2)         # yes (1), no (0)
        self.clc_head = nn.Linear(hidden_dim, num_clc_classes) # 19 BigEarthNet CLC classes
        self.spatial_rel_head = nn.Linear(hidden_dim, 4)    # top, bottom, left, right

    def forward(
        self,
        images: torch.Tensor,              # (B, 3, H, W)
        spectral_features: torch.Tensor,   # (B, 16)
        question_token_ids: torch.Tensor,  # (B, L)
    ) -> Dict[str, torch.Tensor]:
        b = images.size(0)

        # 1. Vision forward pass
        conv_out = self.conv(images)       # (B, 256, 4, 4)
        spatial_tokens = conv_out.flatten(2).transpose(1, 2) # (B, 16, 256)
        spatial_emb = self.spatial_proj(spatial_tokens)       # (B, 16, hidden_dim)

        spectral_emb = self.spectral_proj(spectral_features).unsqueeze(1) # (B, 1, hidden_dim)
        vision_tokens = torch.cat([spatial_emb, spectral_emb], dim=1)     # (B, 17, hidden_dim)

        # 2. Text forward pass
        text_emb = self.token_embed(question_token_ids)      # (B, L, embed_dim)
        text_out, _ = self.text_gru(text_emb)               # (B, L, hidden_dim)
        text_pooled = text_out.mean(dim=1, keepdim=True)    # (B, 1, hidden_dim)

        # 3. Cross-Attention: Question queries Vision
        attn_out, attn_weights = self.cross_attn(
            query=text_pooled,
            key=vision_tokens,
            value=vision_tokens,
        )
        fused_attn = self.layer_norm(text_pooled + attn_out).squeeze(1) # (B, hidden_dim)

        # Concatenate vision summary + attention
        vis_summary = vision_tokens.mean(dim=1)
        multimodal = self.fusion(torch.cat([vis_summary, fused_attn], dim=-1)) # (B, hidden_dim)

        return {
            "mcq_logits": self.mcq_head(multimodal),
            "binary_logits": self.binary_head(multimodal),
            "clc_logits": self.clc_head(multimodal),
            "spatial_logits": self.spatial_rel_head(multimodal),
            "multimodal_embedding": multimodal,
            "attention_weights": attn_weights,
        }
