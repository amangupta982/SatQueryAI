# SatQuery-VQA Codebase Audit Report: Mock & Hardcoded Logic Identification

**Audit Date**: September 11, 2026  
**Auditor**: SatQuery AI Engineering  
**Scope**: Full repository inspection covering `vqa_captioning/`, `frontend_backend/`, `common/`, and configuration files.

---

## 1. Executive Summary

A comprehensive repository audit was conducted to locate all instances of mock, hardcoded, simulated, fallback, or keyword-based VQA answers. The audit confirmed the presence of simulated logic in model inference, training dry-runs, the FastAPI predictor initialization, and the frontend client.

All identified instances will be completely removed and replaced with genuine `BigEarthNet.txt` dataset ingestion, PyTorch + PEFT LoRA training on `Qwen/Qwen2.5-VL-3B-Instruct`, and real model token generation.

---

## 2. Detailed Findings by Component

### A. Model Abstraction & Inference Engine
- **File**: `vqa_captioning/models/satquery_vqa_model.py`
  - **Lines 338–356 (`_mock_predict`)**:
    Contains static keyword-to-answer mappings:
    - `"water"` -> `"Inland waters"` / `"Yes, water bodies are present."`
    - `"vegetation"` / `"forest"` -> `"Broad-leaved forest"` / `"Yes, vegetation is present."`
    - `"urban"` / `"building"` -> `"Urban fabric"` / `"Counting macro land-cover regions..."`
    - `"cover"` / `"dominant"` / `"largest"` -> `"Vegetation is the dominant land cover class."`
    - Default -> `"Coniferous forest"`
  - **Lines 252–262**:
    Invokes `_mock_predict` whenever `self.mock_mode == True`.
  - **Lines 327–337**:
    Catches inference exceptions and reverts to `_mock_predict` instead of raising an honest error.
- **Action**: Completely delete `_mock_predict`. Delete `mock_mode` fallback in `predict()`. Fail explicitly with error status if weights are missing or generation encounters an exception.

### B. Training Pipeline & Smoke Testing
- **File**: `vqa_captioning/training/train_vqa.py`
  - **Lines 88–104 (`DummyVQAHead`)**:
    In `run_dry_run_smoke_test()`, instantiates a trivial 2-layer linear embedding module (`class DummyVQAHead(nn.Module)`) instead of loading the real vision-language model backbone.
  - **Lines 61–74**:
    Uses synthetic smoke test samples (`"Is inland water present in this satellite patch?"`) instead of real `BigEarthNet.txt` samples.
  - **Lines 182–186**:
    Bypasses training loop if `vqa_model.mock_mode == True`.
- **Action**: Delete `DummyVQAHead`. Implement a real multimodal smoke test running real forward and backward passes on `Qwen/Qwen2.5-VL-3B-Instruct` with PEFT LoRA, calculating true language modeling loss on ground-truth answer tokens.

### C. Multimodal Collator
- **File**: `vqa_captioning/training/collator.py`
  - **Lines 49–60**:
    Generates random mock tensors when `self.mock_mode == True` or `self.processor is None`.
- **Action**: Require a valid processor and genuine multimodal inputs; raise an explicit exception if processor is unavailable.

### D. FastAPI Backend Service
- **File**: `frontend_backend/api/vqa_router.py`
  - **Line 30 (`get_vqa_predictor`)**:
    Initializes `SatQueryPredictor(mock_mode=True)` by default.
  - **Missing Status Endpoint**:
    Lacks `GET /api/v1/vqa/status` reporting live checkpoint details and genuine model readiness.
- **Action**: Remove `mock_mode=True`. Load the real fine-tuned adapter checkpoint (`models/satquery-vqa/adapter`). Implement `GET /api/v1/vqa/status`.

### E. Frontend UI Fallbacks
- **File**: `frontend_backend/frontend/src/pages/Dashboard.jsx`
  - **Lines 129–175**:
    In `handleAsk()`, the `catch` block generates simulated answers based on keyword checks (`lower.includes('water')`, etc.) with fabricated confidence scores (`0.925`, `0.968`, `0.954`, etc.).
- **File**: `frontend_backend/frontend/src/pages/VQAWorkspace.jsx`
  - **Lines 125–180**:
    Falls back to `setTimeout` simulated responses with fabricated confidence scores if the backend request fails.
- **Action**: Remove all simulated answer logic in both frontend files. Display the actual backend response or an explicit error state (`● Model unavailable` / `● SatQuery-VQA error`).

---

## 3. Audit Conclusion & Next Steps

All identified locations have been cataloged. The implementation will systematically remove every mock path, download and inspect the real `BigEarthNet.txt` dataset, configure PEFT LoRA on `Qwen/Qwen2.5-VL-3B-Instruct`, execute a real smoke test, verify parameter updates, and connect the live model to the FastAPI endpoint.
