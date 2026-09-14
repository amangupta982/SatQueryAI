"""
Dataset Adapters for Unified Multitemporal Change Intelligence.
Converts heterogeneous dataset annotations into TemporalVQASample instances.
"""

from .base import (
    BaseChangeDataset,
    MultitemporalVQADataset,
    SemanticChangeDataset,
    ChangeGroundingDataset,
    GeneralRemoteSensingVQADataset,
)
from .changechat_adapter import ChangeChatAdapter
from .rsrcc_adapter import RSRCCAdapter
from .second_adapter import SECONDAdapter
from .qag360k_adapter import QAG360KAdapter
from .bigearthnet_adapter import BigEarthNetAdapter
from .bigearthnet_txt_adapter import BigEarthNetTxtDataset
from .rsvlmqa_adapter import RSVLMQAAdapter

