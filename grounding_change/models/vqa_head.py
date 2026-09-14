"""
Temporal Visual Question Answering (VQA) Head.
Predicts natural language answers from visual temporal difference representations
and natural language query embeddings.
"""

from typing import List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


class TemporalVQAHead(nn.Module):
    """
    Multimodal classification / prediction head for VQA.
    Combines pooled visual features with question embeddings.
    """

    def __init__(self, visual_dim: int = 256, text_dim: int = 256, num_answers: int = 1000):
        super().__init__()
        self.visual_pool = nn.AdaptiveAvgPool2d(1)
        self.fusion = nn.Sequential(
            nn.Linear(visual_dim + text_dim, 512),
            nn.LayerNorm(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(512, 512),
            nn.LayerNorm(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(512, num_answers)
        )

    def forward(self, visual_feat: torch.Tensor, text_feat: torch.Tensor) -> torch.Tensor:
        """
        visual_feat: (B, C, H, W)
        text_feat: (B, text_dim)
        Returns:
            logits: (B, num_answers)
        """
        v_pooled = self.visual_pool(visual_feat).flatten(1)  # (B, C)
        combined = torch.cat([v_pooled, text_feat], dim=1)
        logits = self.fusion(combined)
        return logits
