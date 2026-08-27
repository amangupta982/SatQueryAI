# VQA & Captioning Module

**Owner**: Person 3

**Purpose**:
Performs Visual Question Answering (VQA) and generates textual captions for satellite imagery.

**Responsibilities**:
- Tokenizer
- Text decoder
- Multimodal projection
- VQA
- Captioning
- Fine-tuning
- Evaluation
- Inference

**Expected Inputs**:
- Visual embeddings (Optical/Fused), Text queries.

**Expected Outputs**:
- Textual answers, generated captions.

**Planned Models/Components**:
- Multimodal projector, LLM/Text Decoder.

**Dataset(s) to be used**:
- RSVQA, Custom captioning datasets.

**Training plan**:
- Instruction fine-tuning on VQA pairs.

**Evaluation metrics**:
- BLEU, METEOR, CIDEr, Exact Match for VQA.

**Inference plan**:
- Generative text pipeline conditioned on image embeddings.

**Integration points with other modules**:
- Consumes visual embeddings from `optical_vision` or `sar_fusion`, called by `agent_rag`.

**Expected API/interface**:
- `generate_answer(image_embeds, question)`

**Development checklist**:
- [ ] Define tokenizer strategy
- [ ] Define projection and decoder architecture
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
