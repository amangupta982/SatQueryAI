"""
Question-Conditioned Visual Grounding Head.
Given textual query features and visual temporal difference features,
predicts a spatial grounding heatmap/mask highlighting only query-relevant change regions.
"""

from typing import List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleTextEncoder(nn.Module):
    """
    Lightweight learned text embedder that maps character/token n-grams or word IDs
    into a query embedding vector of dimension text_dim.
    """

    def __init__(self, vocab_size: int = 5000, text_dim: int = 256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, text_dim, padding_idx=0)
        self.lstm = nn.GRU(text_dim, text_dim // 2, batch_first=True, bidirectional=True)
        self.proj = nn.Linear(text_dim, text_dim)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        """token_ids: (B, L) -> returns (B, text_dim)"""
        emb = self.embedding(token_ids)
        _, h_n = self.lstm(emb)
        # Concatenate forward and backward hidden states -> (B, text_dim)
        h = torch.cat([h_n[0], h_n[1]], dim=-1)
        return self.proj(h)


class QuestionConditionedGroundingHead(nn.Module):
    """
    Cross-attends question representation with temporal visual features
    to generate query-specific visual grounding masks.
    """

    def __init__(self, visual_dim: int = 256, text_dim: int = 256):
        super().__init__()
        self.text_proj = nn.Linear(text_dim, visual_dim)

        self.cross_conv = nn.Sequential(
            nn.Conv2d(visual_dim * 2, visual_dim, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(visual_dim),
            nn.ReLU(inplace=True),
            nn.Conv2d(visual_dim, visual_dim // 2, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(visual_dim // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(visual_dim // 2, 1, kernel_size=1)
        )

    def forward(
        self,
        fused_visual_feat: torch.Tensor,
        text_embedding: torch.Tensor,
        target_size: Tuple[int, int]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        fused_visual_feat: (B, C, H_feat, W_feat)
        text_embedding: (B, text_dim)
        target_size: (H, W)
        Returns:
            logits: (B, 1, H, W)
            prob: (B, 1, H, W)
        """
        b, c, h, w = fused_visual_feat.shape
        proj_text = self.text_proj(text_embedding).unsqueeze(-1).unsqueeze(-1)  # (B, C, 1, 1)
        expanded_text = proj_text.expand(-1, -1, h, w)

        combined = torch.cat([fused_visual_feat, expanded_text], dim=1)
        ground_logits_low = self.cross_conv(combined)

        # Upsample to target size
        logits = F.interpolate(ground_logits_low, size=target_size, mode="bilinear", align_corners=False)
        prob = torch.sigmoid(logits)

        return logits, prob
