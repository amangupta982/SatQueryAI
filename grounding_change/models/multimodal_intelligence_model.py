"""
Optical-SAR Multimodal Intelligence Model
Unified Foundation Architecture for BigEarthNet.txt (arXiv:2603.29630)
Integrates Prithvi-EO-2.0-300M Optical ViT and SUMMIT SAR ViT via Cross-Attention Fusion.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import torch
import torch.nn as nn
import torch.nn.functional as F

from grounding_change.config import settings
from grounding_change.taxonomy import taxonomy
from .prithvi_encoder import PrithviEO2OpticalEncoder
from .summit_sar_encoder import SummitSAREncoder
from .optical_sar_fusion import OpticalSARFusionModule

logger = logging.getLogger("MultimodalIntelligenceModel")


class SimpleTextEncoder(nn.Module):
    """Encodes query or referring expression instructions into semantic text vectors."""

    def __init__(self, vocab_size: int = 5000, embed_dim: int = 256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.gru = nn.GRU(embed_dim, embed_dim // 2, batch_first=True, bidirectional=True)
        self.proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        # input_ids: (B, seq_len)
        embedded = self.embedding(input_ids)
        _, h_n = self.gru(embedded)
        # h_n: (2, B, embed_dim // 2) -> (B, embed_dim)
        text_vec = torch.cat([h_n[0], h_n[1]], dim=-1)
        return self.proj(text_vec)


class BigEarthNetVQAHead(nn.Module):
    """
    Visual Question Answering head covering BigEarthNet.txt 15 tasks:
    Presence, Area, Counting, Adjacency, Relative Position, Country, Season, Climate Zone.
    """

    def __init__(self, visual_dim: int = 256, text_dim: int = 256, hidden_dim: int = 512, num_answers: int = 1000):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.Linear(visual_dim + text_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, num_answers)
        )

    def forward(self, visual_feature: torch.Tensor, text_feature: torch.Tensor) -> torch.Tensor:
        # visual_feature: (B, visual_dim)
        # text_feature: (B, text_dim)
        joint = torch.cat([visual_feature, text_feature], dim=-1)
        return self.classifier(joint)


class VisualGroundingHead(nn.Module):
    """
    Referring expression visual grounding head.
    Cross-attends natural language instruction tokens with multiscale spatial features
    to output localized bounding boxes and segmentation masks.
    """

    def __init__(self, feature_dim: int = 256, text_dim: int = 256):
        super().__init__()
        self.conv_align = nn.Conv2d(feature_dim, feature_dim, kernel_size=1)
        self.text_proj = nn.Linear(text_dim, feature_dim)
        self.decoder = nn.Sequential(
            nn.Conv2d(feature_dim, feature_dim // 2, kernel_size=3, padding=1),
            nn.BatchNorm2d(feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(feature_dim // 2, feature_dim // 4, kernel_size=4, stride=4),
            nn.BatchNorm2d(feature_dim // 4),
            nn.ReLU(inplace=True),
            nn.Conv2d(feature_dim // 4, 1, kernel_size=1),
            nn.Sigmoid()
        )
        # Box regression head: [ymin, xmin, ymax, xmax] normalized
        self.bbox_regressor = nn.Sequential(
            nn.Linear(feature_dim, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 4),
            nn.Sigmoid()
        )

    def forward(self, spatial_feature: torch.Tensor, text_feature: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # spatial_feature: (B, feature_dim, H/4, W/4)
        # text_feature: (B, text_dim)
        B, C, H, W = spatial_feature.shape
        f_vis = self.conv_align(spatial_feature)
        t_proj = self.text_proj(text_feature).view(B, C, 1, 1)

        # Spatial-text modulation
        modulated = f_vis * t_proj
        grounding_mask = self.decoder(modulated)  # (B, 1, H, W)

        # Global pooled visual-text vector for bbox coordinates
        pooled = modulated.mean(dim=[2, 3])
        pred_bboxes = self.bbox_regressor(pooled)  # (B, 4)

        return grounding_mask, pred_bboxes


class LandCoverSemanticHead(nn.Module):
    """
    7-Class LULC Semantic Segmentation Head for European land cover
    (Built Environment, Vegetation, Low Veg, Water, Bare Land, Infrastructure, Background).
    """

    def __init__(self, feature_dim: int = 256, num_classes: int = 7):
        super().__init__()
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(feature_dim, feature_dim // 2, kernel_size=4, stride=4),
            nn.BatchNorm2d(feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(feature_dim // 2, num_classes, kernel_size=1)
        )

    def forward(self, spatial_feature: torch.Tensor) -> torch.Tensor:
        # spatial_feature: (B, feature_dim, H/4, W/4)
        logits = self.decoder(spatial_feature)  # (B, num_classes, H, W)
        return logits


class MultimodalIntelligenceModel(nn.Module):
    """
    Unified Optical-SAR Multimodal Agent Architecture.
    Trained and evaluated strictly on BigEarthNet.txt.
    """

    def __init__(
        self,
        optical_in_channels: int = 6,
        sar_in_channels: int = 2,
        feature_dim: int = 256,
        num_classes: int = 7,
        num_vqa_answers: int = 1000,
        optical_weights_path: Optional[str] = None,
        sar_weights_path: Optional[str] = None,
    ):
        super().__init__()
        self.feature_dim = feature_dim
        self.num_classes = num_classes

        # 1. Optical Branch Foundation Encoder (Prithvi-EO-2.0-300M)
        self.optical_encoder = PrithviEO2OpticalEncoder(
            in_channels=optical_in_channels,
            feature_dim=feature_dim,
            pretrained_weights_path=optical_weights_path
        )

        # 2. SAR Branch Foundation Encoder (SUMMIT SAR ViT)
        self.sar_encoder = SummitSAREncoder(
            in_channels=sar_in_channels,
            feature_dim=feature_dim,
            pretrained_weights_path=sar_weights_path
        )

        # 3. Cross-Modal Alignment & Attention Fusion
        self.fusion = OpticalSARFusionModule(
            feature_dim=feature_dim,
            num_heads=8,
            dropout=0.1
        )

        # 4. Text Instruction Encoder
        self.text_encoder = SimpleTextEncoder(embed_dim=feature_dim)

        # 5. Task Heads
        self.vqa_head = BigEarthNetVQAHead(
            visual_dim=feature_dim,
            text_dim=feature_dim,
            num_answers=num_vqa_answers
        )
        self.grounding_head = VisualGroundingHead(
            feature_dim=feature_dim,
            text_dim=feature_dim
        )
        self.semantic_head = LandCoverSemanticHead(
            feature_dim=feature_dim,
            num_classes=num_classes
        )

    def forward(
        self,
        optical_tensor: Optional[torch.Tensor] = None,
        sar_tensor: Optional[torch.Tensor] = None,
        text_tokens: Optional[torch.Tensor] = None,
        mode: str = "optical_sar"
    ) -> Dict[str, Any]:
        """
        Forward pass supporting 7 agent operational modes:
        optical_only, sar_only, optical_sar, optical_sar_vqa, optical_sar_vqa_grounding, etc.
        """
        device = next(self.parameters()).device
        outputs: Dict[str, Any] = {}

        # 1. Optical-only path
        f_opt = None
        if optical_tensor is not None:
            f_opt = self.optical_encoder(optical_tensor)
            outputs["optical_features"] = f_opt

        # 2. SAR-only path
        f_sar = None
        if sar_tensor is not None:
            f_sar = self.sar_encoder(sar_tensor)
            outputs["sar_features"] = f_sar

        # 3. Multimodal Fusion (when both are supplied)
        fused_outputs = None
        if f_opt is not None and f_sar is not None:
            fused_outputs = self.fusion(f_opt, f_sar)
            outputs["fusion"] = fused_outputs
            spatial_feature = fused_outputs["F_fused"]["p2"]
            global_visual_feature = fused_outputs["F_fused"]["global_feature"]
            outputs["cross_modal_diff_map"] = fused_outputs["cross_modal_diff_map"]
        elif f_opt is not None:
            spatial_feature = f_opt["p2"]
            global_visual_feature = f_opt["global_feature"]
        elif f_sar is not None:
            spatial_feature = f_sar["p2"]
            global_visual_feature = f_sar["global_feature"]
        else:
            raise ValueError("At least one modality (optical or SAR) must be provided.")

        # 4. Dense Semantic Land Cover Prediction
        semantic_logits = self.semantic_head(spatial_feature)
        outputs["semantic_logits"] = semantic_logits
        outputs["semantic_probs"] = F.softmax(semantic_logits, dim=1)

        # 5. Text processing (for VQA and Referring Expressions)
        if text_tokens is not None:
            text_feat = self.text_encoder(text_tokens)
            outputs["text_feature"] = text_feat

            # VQA Logits
            vqa_logits = self.vqa_head(global_visual_feature, text_feat)
            outputs["vqa_logits"] = vqa_logits
            outputs["vqa_probs"] = F.softmax(vqa_logits, dim=-1)

            # Grounding Mask & Bounding Box Regression
            grounding_mask, pred_bboxes = self.grounding_head(spatial_feature, text_feat)
            outputs["grounding_mask"] = grounding_mask
            outputs["pred_bboxes"] = pred_bboxes

        return outputs
