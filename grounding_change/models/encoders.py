"""
Shared-Weight Siamese Temporal Encoder.
Extracts hierarchical multi-scale visual features from T1 and T2 using shared weights.
"""

from typing import Dict, List, Optional, Tuple
import torch
import torch.nn as nn
import torchvision.models as models


class SiameseTemporalEncoder(nn.Module):
    """
    Siamese backbone that encodes T1 and T2 images through identical shared weights.
    Yields multi-scale feature maps at 1/4, 1/8, 1/16, and 1/32 spatial resolutions.
    """

    def __init__(self, backbone_name: str = "resnet50", pretrained: bool = True):
        super().__init__()
        self.backbone_name = backbone_name

        # Load ResNet backbone
        try:
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            resnet = models.resnet50(weights=weights)
        except Exception:
            # Offline or fallback mode
            resnet = models.resnet50(weights=None)

        # Split into progressive multi-scale stages
        self.conv1 = resnet.conv1
        self.bn1 = resnet.bn1
        self.relu = resnet.relu
        self.maxpool = resnet.maxpool

        self.layer1 = resnet.layer1  # 256 channels, 1/4 scale
        self.layer2 = resnet.layer2  # 512 channels, 1/8 scale
        self.layer3 = resnet.layer3  # 1024 channels, 1/16 scale
        self.layer4 = resnet.layer4  # 2048 channels, 1/32 scale

        self.out_channels = [256, 512, 1024, 2048]

    def forward_single(self, x: torch.Tensor) -> List[torch.Tensor]:
        """Pass one temporal image through backbone."""
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        c2 = self.layer1(x)
        c3 = self.layer2(c2)
        c4 = self.layer3(c3)
        c5 = self.layer4(c4)

        return [c2, c3, c4, c5]

    def forward(
        self,
        t1: torch.Tensor,
        t2: Optional[torch.Tensor] = None
    ) -> Tuple[List[torch.Tensor], Optional[List[torch.Tensor]]]:
        """
        Extract multi-scale features for T1 and T2.
        If T2 is None, runs single-image feature extraction.
        """
        f1 = self.forward_single(t1)
        f2 = self.forward_single(t2) if t2 is not None else None
        return f1, f2
