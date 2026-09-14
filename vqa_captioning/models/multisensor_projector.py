"""
Multi-sensor projection adapter for Earth Observation data.
Aligns Sentinel-1 SAR and Sentinel-2 Multispectral patch representations
with the Vision-Language Model embedding space.
Reference: BigEarthNet.txt (arXiv:2603.29630, Section 4.2).
"""

import torch
import torch.nn as nn
from typing import Optional, Tuple

class MultiSensorProjector(nn.Module):
    """
    Projects multi-band optical (Sentinel-2) and SAR (Sentinel-1) visual features
    into the token embedding space of the language model backbone.
    """

    def __init__(
        self,
        s2_input_dim: int = 768,
        s1_input_dim: int = 768,
        llm_hidden_dim: int = 2048,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.s2_input_dim = s2_input_dim
        self.s1_input_dim = s1_input_dim
        self.llm_hidden_dim = llm_hidden_dim

        # Sentinel-2 Multispectral Projection (10m + 20m bands)
        self.s2_projector = nn.Sequential(
            nn.Linear(s2_input_dim, llm_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(llm_hidden_dim, llm_hidden_dim),
            nn.LayerNorm(llm_hidden_dim),
        )

        # Sentinel-1 SAR Projection (VV + VH dual-polarization)
        self.s1_projector = nn.Sequential(
            nn.Linear(s1_input_dim, llm_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(llm_hidden_dim, llm_hidden_dim),
            nn.LayerNorm(llm_hidden_dim),
        )

    def forward(
        self,
        s2_features: Optional[torch.Tensor] = None,
        s1_features: Optional[torch.Tensor] = None,
    ) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor]]:
        """
        Args:
            s2_features: (batch_size, num_patches, s2_input_dim)
            s1_features: (batch_size, num_patches, s1_input_dim)
        Returns:
            Tuple of projected embeddings (s2_tokens, s1_tokens) in llm_hidden_dim space.
        """
        s2_tokens = None
        s1_tokens = None

        if s2_features is not None:
            s2_tokens = self.s2_projector(s2_features)

        if s1_features is not None:
            s1_tokens = self.s1_projector(s1_features)

        return s2_tokens, s1_tokens
