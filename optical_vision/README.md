# Optical Vision Module

**Owner**: Person 1

**Purpose**:
Handles processing and feature extraction for optical satellite imagery.

**Responsibilities**:
- Optical satellite image preprocessing
- ViT/CNN optical encoder
- Contrastive pretraining
- Optical feature extraction
- Training and evaluation
- Inference

**Expected Inputs**:
- Raw or normalized optical satellite images.

**Expected Outputs**:
- Processed optical embeddings/features.

**Planned Models/Components**:
- ViT/CNN encoders.

**Dataset(s) to be used**:
- BigEarthNet, VRSBench (Optical portions)

**Training plan**:
- Contrastive pretraining on optical imagery.

**Evaluation metrics**:
- Precision, Recall, F1 for optical feature classification/retrieval.

**Inference plan**:
- Extract features for given optical images.

**Integration points with other modules**:
- Features consumed by `vqa_captioning`, `grounding_change`, and `sar_fusion`.

**Expected API/interface**:
- `extract_optical_features(image)`

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
