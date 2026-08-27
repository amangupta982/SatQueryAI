# SAR Fusion Module

**Owner**: Person 2

**Purpose**:
Handles processing of Synthetic Aperture Radar (SAR) imagery and fuses it with optical features.

**Responsibilities**:
- SAR preprocessing
- SAR encoder
- Optical-SAR alignment
- Cross-attention / multimodal fusion
- Fusion training
- Evaluation
- Inference

**Expected Inputs**:
- SAR imagery, optical embeddings.

**Expected Outputs**:
- Fused Optical-SAR embeddings/features.

**Planned Models/Components**:
- SAR encoder (CNN/ViT), Cross-attention fusion module.

**Dataset(s) to be used**:
- BigEarthNet (SAR portions), aligned Optical-SAR datasets.

**Training plan**:
- Contrastive learning for alignment, cross-attention training.

**Evaluation metrics**:
- Alignment accuracy, retrieval metrics across modalities.

**Inference plan**:
- Extract SAR features and yield fused embeddings.

**Integration points with other modules**:
- Consumes optical features from `optical_vision`. Fused features used by downstream tasks.

**Expected API/interface**:
- `extract_sar_features(sar_image)`
- `fuse_features(optical_feat, sar_feat)`

**Development checklist**:
- [ ] Define model architecture
- [ ] Add preprocessing pipeline
- [ ] Add training pipeline
- [ ] Add evaluation
- [ ] Add inference
- [ ] Expose integration interface

**TODO**:
- [ ] Define model architecture
- [ ] Add preprocessing pipeline
- [ ] Add training pipeline
- [ ] Add evaluation
- [ ] Add inference
- [ ] Expose integration interface
