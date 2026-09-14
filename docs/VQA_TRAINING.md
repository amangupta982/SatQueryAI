# SatQuery-VQA: Training, Evaluation & Deployment Guide

This guide documents the full training pipeline, parameter-efficient fine-tuning (LoRA / QLoRA), evaluation on BigEarthNet.txt benchmarks, standalone inference, and FastAPI backend integration for **SatQuery-VQA**.

---

## 1. Quick Start & CLI Workflows

### 1.1 Inspecting the Dataset
Audits directory structure, checks image file integrity, verifies task annotations, and detects duplicate IDs:
```bash
python vqa_captioning/scripts/run_inspect.py \
    --dataset /path/to/BigEarthNet.txt
```

### 1.2 Preparing & Validating Dataset Splits
Parses raw BigEarthNet annotations into the unified SatQuery schema, validates image paths, and exports split files (`train.json`, `validation.json`, `benchmark.json`):
```bash
python vqa_captioning/scripts/run_prepare.py \
    --dataset /path/to/BigEarthNet.txt \
    --output-dir data/prepared_satquery_vqa
```

### 1.3 Smoke Testing the Training Pipeline
Runs an end-to-end forward/backward optimization pass, saves a temporary checkpoint, reloads it, and tests inference without downloading full weights:
```bash
python vqa_captioning/scripts/run_train.py --dry-run
```

### 1.4 Full Model Training (LoRA / QLoRA)
Fine-tunes the foundation VLM using LoRA or 4-bit QLoRA:
```bash
# Standard 16-bit LoRA (for 24GB+ GPUs like A10G, RTX 4090, A100)
python vqa_captioning/scripts/run_train.py \
    --config vqa_captioning/configs/base_config.yaml

# 4-bit QLoRA (for 16GB-24GB GPUs or single consumer cards)
python vqa_captioning/scripts/run_train.py \
    --config vqa_captioning/configs/qlora_qwen_3b.yaml
```

### 1.5 Resuming Interrupted Training
```bash
python vqa_captioning/scripts/run_train.py \
    --config vqa_captioning/configs/qlora_qwen_3b.yaml \
    --resume outputs/satquery-vqa-qlora/checkpoints/checkpoint_step_200
```

### 1.6 Evaluating on BigEarthNet Benchmark Split
Calculates Exact Match, Accuracy, Macro F1, MAE/RMSE for counting, and IoU for bounding boxes:
```bash
python vqa_captioning/scripts/run_evaluate.py \
    --split data/prepared_satquery_vqa/benchmark.json \
    --adapter outputs/satquery-vqa-qlora/adapter \
    --output-report outputs/benchmark_evaluation_report.md
```

### 1.7 Running Standalone Inference
```bash
# Interactive CLI query
python vqa_captioning/scripts/run_inference.py \
    --image /path/to/satellite_patch.png \
    --question "What is the dominant land-cover type?" \
    --sensor Sentinel-2
```

---

## 2. Hardware & GPU Requirements

| Training Mode | Precision | Target Hardware | Minimum VRAM | Recommended Batch Size |
|---|---|---|---|---|
| **QLoRA (4-bit)** | NF4 / BF16 | RTX 3080/4070/4090, T4, A10G | 8 GB | 1–2 (Grad Accum: 16) |
| **LoRA (16-bit)** | BF16 / FP16 | RTX 4090 (24GB), A10G, A100 | 16 GB | 2–4 (Grad Accum: 8) |
| **Local Testing** | FP32 / FP16 | Apple Silicon (M1/M2/M3/M4) | 16 GB unified RAM | 1 (Grad Accum: 4) |

---

## 3. Key Hyperparameters (`vqa_captioning/configs/`)

- **LoRA Rank ($r$)**: `16` (Base) / `8` (QLoRA)
- **LoRA Alpha ($\alpha$)**: `32`
- **LoRA Dropout**: `0.05`–`0.1`
- **Learning Rate**: `1e-4` (Cosine annealing schedule with linear warmup)
- **Warmup Ratio**: `0.03`
- **Weight Decay**: `0.01`
- **Gradient Accumulation**: `8`–`16`
- **Gradient Checkpointing**: Enabled

---

## 4. FastAPI Backend Integration

The model is exposed to the SatQuery AI backend via `frontend_backend/api/vqa_router.py`.

### Start Backend Dev Server:
```bash
uvicorn frontend_backend.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Endpoint Contract:
`POST /api/v1/vqa`

**Input**:
- `question` (Form text)
- `image` (Multipart file) or `image_b64` (Base64 string)
- `sensor` (`Sentinel-2` or `Sentinel-1`)

**Output JSON**:
```json
{
  "answer": "Vegetation is the dominant land-cover type.",
  "confidence": null,
  "task": "presence",
  "evidence": {
    "sensor": "Sentinel-2"
  },
  "model": "SatQuery-VQA"
}
```

---

## 5. Verification Suite

Execute the complete automated test suite:
```bash
pytest vqa_captioning/tests/ -v
```
All 23 unit tests validate dataset parsing, sample validation, sensor adapters, collator batching, model loading, counting limitation routing, area calculation, evidence extraction, and FastAPI routing.
