"""
Master Change Intelligence Model.
Integrates Siamese temporal encoders, multi-scale temporal fusion,
binary change segmentation, semantic land-cover classification,
transition prediction, visual grounding, and temporal VQA heads.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import torch
import torch.nn as nn
from ..config import settings
from ..taxonomy import taxonomy
from .encoders import SiameseTemporalEncoder
from .temporal_fusion import TemporalFusionModule
from .change_detector import BinaryChangeHead
from .semantic_segmentor import SemanticSegmentationHead
from .transition_predictor import TransitionPredictionHead
from .vqa_head import TemporalVQAHead
from ..grounding.grounding_head import QuestionConditionedGroundingHead, SimpleTextEncoder


class ChangeIntelligenceModel(nn.Module):
    """
    Unified multimodal neural architecture for remote-sensing change intelligence.
    Supports bi-temporal change analysis, zero-question comprehensive representation,
    question-conditioned grounding, and single-image remote-sensing VQA.
    """

    def __init__(
        self,
        backbone_name: str = "resnet50",
        pretrained: bool = True,
        feature_dim: int = 256,
        text_dim: int = 256,
        num_classes: Optional[int] = None,
        num_answers: int = 1000,
    ):
        super().__init__()
        self.num_classes = num_classes or taxonomy.num_classes
        self.feature_dim = feature_dim
        self.text_dim = text_dim

        # 1. Siamese Shared-Weight Temporal Encoder
        self.encoder = SiameseTemporalEncoder(backbone_name=backbone_name, pretrained=pretrained)
        in_channels = self.encoder.out_channels  # [256, 512, 1024, 2048]

        # 2. Temporal Fusion (Fdiff, Fabs, Fcat)
        self.fusion = TemporalFusionModule(in_channels=in_channels, feature_dim=feature_dim)

        # 3. Output Heads
        self.change_head = BinaryChangeHead(feature_dim=feature_dim, num_levels=len(in_channels))
        self.semantic_head = SemanticSegmentationHead(in_dim=feature_dim, num_classes=self.num_classes)
        self.transition_head = TransitionPredictionHead(in_dim=feature_dim, num_classes=self.num_classes)

        # 4. Multimodal Heads (Grounding & VQA)
        self.text_encoder = SimpleTextEncoder(vocab_size=8000, text_dim=text_dim)
        self.grounding_head = QuestionConditionedGroundingHead(visual_dim=feature_dim, text_dim=text_dim)
        self.vqa_head = TemporalVQAHead(visual_dim=feature_dim, text_dim=text_dim, num_answers=num_answers)

    def _tokenize_text(self, text: Union[str, List[str]], device: torch.device) -> torch.Tensor:
        """Simple deterministic token indexer for textual questions."""
        if isinstance(text, str):
            text = [text]
        max_len = 32
        token_batch = []
        for t in text:
            words = t.lower().replace("?", "").replace(".", "").split()
            ids = [abs(hash(w)) % 7999 + 1 for w in words[:max_len]]
            if len(ids) < max_len:
                ids += [0] * (max_len - len(ids))
            token_batch.append(ids)
        return torch.tensor(token_batch, dtype=torch.long, device=device)

    def forward(
        self,
        t1: torch.Tensor,
        t2: Optional[torch.Tensor] = None,
        question: Optional[Union[str, List[str], torch.Tensor]] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive forward pass.

        Args:
            t1: (B, 3, H, W) Image T1
            t2: (B, 3, H, W) Image T2 (None for single-image mode)
            question: Optional natural language question(s)

        Returns:
            Dictionary containing logits, probabilities, masks, and representations.
        """
        b, c, h, w = t1.shape
        target_size = (h, w)
        device = t1.device

        # Single-image remote sensing mode
        if t2 is None:
            f1_levels, _ = self.encoder(t1, None)
            # Project finest level for semantic prediction
            proj = nn.functional.interpolate(f1_levels[0], size=(h // 4, w // 4), mode="bilinear", align_corners=False)
            sem_logits_t1, sem_probs_t1 = self.semantic_head(f1_levels[0], target_size)
            outputs = {
                "sem_logits_t1": sem_logits_t1,
                "sem_probs_t1": sem_probs_t1,
                "is_temporal": False,
            }
            if question is not None:
                token_ids = self._tokenize_text(question, device) if isinstance(question, (str, list)) else question
                text_emb = self.text_encoder(token_ids)
                vqa_logits = self.vqa_head(f1_levels[0], text_emb)
                outputs["vqa_logits"] = vqa_logits
            return outputs

        # 1. Siamese Encoding
        f1_levels, f2_levels = self.encoder(t1, t2)

        # 2. Temporal Fusion (Fdiff, Fabs, Fcat)
        fused_levels = self.fusion(f1_levels, f2_levels)
        finest_fused = fused_levels[0]  # 1/4 resolution feature map

        # 3. Binary Change Detection
        change_logits, change_probs = self.change_head(fused_levels, target_size)

        # 4. Semantic Land-Cover (T1 and T2)
        sem_logits_t1, sem_probs_t1 = self.semantic_head(f1_levels[0], target_size)
        sem_logits_t2, sem_probs_t2 = self.semantic_head(f2_levels[0], target_size)

        # 5. Semantic Transitions
        trans_logits, trans_probs = self.transition_head(finest_fused, target_size)

        # 6. Feature-level temporal difference representation
        f_diff = f2_levels[-1] - f1_levels[-1]
        feat_change_score = torch.norm(f_diff, dim=1, keepdim=True)
        feat_change_score = nn.functional.interpolate(feat_change_score, size=target_size, mode="bilinear", align_corners=False)

        outputs = {
            "is_temporal": True,
            "change_logits": change_logits,
            "change_probs": change_probs,
            "sem_logits_t1": sem_logits_t1,
            "sem_probs_t1": sem_probs_t1,
            "sem_logits_t2": sem_logits_t2,
            "sem_probs_t2": sem_probs_t2,
            "trans_logits": trans_logits,
            "trans_probs": trans_probs,
            "feature_change_score": feat_change_score,
            "fused_features": finest_fused,
        }

        # 7. Question-conditioned Grounding and VQA (if query supplied)
        if question is not None:
            token_ids = self._tokenize_text(question, device) if isinstance(question, (str, list)) else question
            text_emb = self.text_encoder(token_ids)
            ground_logits, ground_probs = self.grounding_head(finest_fused, text_emb, target_size)
            vqa_logits = self.vqa_head(finest_fused, text_emb)

            outputs["ground_logits"] = ground_logits
            outputs["ground_probs"] = ground_probs
            outputs["vqa_logits"] = vqa_logits
            outputs["text_embedding"] = text_emb

        return outputs
