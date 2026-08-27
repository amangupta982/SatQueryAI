# Grounding & Change Detection Module

**Owner**: Person 4

**Purpose**:
Performs spatial understanding tasks: object grounding (bounding boxes/masks) and change detection across temporal image pairs.

**Responsibilities**:
- Object grounding
- Bounding-box prediction
- Mask/segmentation support
- Change detection
- Change-VQA
- Training
- Evaluation
- Inference

**Expected Inputs**:
- Single or temporal pairs of image embeddings, textual queries.

**Expected Outputs**:
- Bounding box coordinates, segmentation masks, change maps, change descriptions.

**Planned Models/Components**:
- Detection/Segmentation head, Temporal comparison module.

**Dataset(s) to be used**:
- CDVQA, object detection benchmarks.

**Training plan**:
- Fine-tuning detection heads, contrastive temporal training.

**Evaluation metrics**:
- mAP, IoU, F1-score for change detection.

**Inference plan**:
- Yield bounding boxes or change masks given image(s).

**Integration points with other modules**:
- Consumes embeddings, outputs bounding boxes/masks to `frontend_backend` for rendering.

**Expected API/interface**:
- `detect_objects()`
- `detect_changes()`

**Development checklist**:
- [ ] Define grounding architecture
- [ ] Define change detection architecture
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
