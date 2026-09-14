# SatQuery-VQA: Base Foundation Model Selection & Technical Analysis

**Document**: `docs/model_selection.md`  
**Model Name**: SatQuery-VQA  
**Selected Foundation Backbone**: **Qwen2.5-VL-3B-Instruct** (`Qwen/Qwen2.5-VL-3B-Instruct`)  
**Low-VRAM Alternative Backbone**: **Qwen2-VL-2B-Instruct** (`Qwen/Qwen2-VL-2B-Instruct`)  

---

## 1. Selected Model Overview

| Parameter | Primary Backbone (`Qwen2.5-VL-3B-Instruct`) | Low-VRAM Backbone (`Qwen2-VL-2B-Instruct`) |
|---|---|---|
| **Parameters** | 3.09 Billion | 2.21 Billion |
| **Architecture** | Vision Transformer (ViT) + Window Attention + Qwen2.5 Decoder | ViT (NaViT style dynamic patch) + Qwen2 Decoder |
| **Context Length** | Up to 32,768 tokens | Up to 32,768 tokens |
| **Native Grounding** | Tokens `[ymin, xmin, ymax, xmax]` normalized to [0, 1000] | Tokens `[ymin, xmin, ymax, xmax]` normalized to [0, 1000] |
| **Resolution Handling** | Dynamic Native Resolution (no fixed square padding distortion) | Dynamic Native Resolution |
| **Hugging Face Class** | `Qwen2_5_VLForConditionalGeneration` / `AutoProcessor` | `Qwen2VLForConditionalGeneration` / `AutoProcessor` |
| **PEFT / LoRA Support** | Fully supported in Hugging Face `peft` (target modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`) | Fully supported in `peft` |
| **Quantization** | BitsAndBytes 4-bit (NF4) / 8-bit | BitsAndBytes 4-bit / 8-bit |
| **License** | **Apache 2.0** (Open Commercial & Academic Use) | **Apache 2.0** |

---

## 2. Why Qwen2.5-VL is the Optimal Choice for SatQuery AI

1. **Native Remote-Sensing Dynamic Aspect Ratio**:
   Standard Sentinel-2 satellite tiles are 120 × 120 pixels. Conventional fixed-resolution VLMs (like CLIP or older LLaVA architectures) force image resizing to 224 × 224 or 336 × 336 with bi-cubic interpolation, introducing spatial blur and aspect distortion. Qwen2.5-VL natively processes dynamic patch grids (`smart_resize`), preserving raw remote-sensing pixel spatial fidelity.
2. **First-Class Spatial Grounding Tokens**:
   BigEarthNet.txt includes **referring expression detection** (Task 6), requiring models to localize land-cover instances using bounding boxes `[ymin, xmin, ymax, xmax]`. Qwen2.5-VL was pre-trained directly on coordinate tokens in the text sequence, enabling accurate localization without needing an external detection head.
3. **Compute Budget & VRAM Efficiency**:
   With 4-bit QLoRA, `Qwen2.5-VL-3B-Instruct` fits within **~6.5 GB of VRAM**, making it trainable on single consumer GPUs (RTX 3080/4070/4090, Apple Silicon MPS for testing, or cloud T4/A10G). Full 16-bit BF16 LoRA fine-tuning fits comfortably on an A10G (24 GB) or A100.
4. **Permissive Open-Source License**:
   The Apache 2.0 license grants unrestricted academic and commercial deployment rights for the SatQuery AI platform.

---

## 3. Alternative Candidates Evaluated

| Model | Evaluation Result | Reason Not Chosen as Primary |
|---|---|---|
| **InternVL-3-1B / InternVL2.5-2B** | *Strong Contender* (used as RS-InternVL in BigEarthNet.txt paper) | Highly competitive, but has custom model dependencies and slightly less standardized Hugging Face text coordinate tokenization for bounding boxes. We provide an architectural adapter interface to support it as a multi-sensor branch. |
| **SmolVLM-Instruct (2.2B)** | *Feasible* | Fast inference and very small footprint, but lacks coordinate token pre-training for bounding box grounding. |
| **PaliGemma-2 (3B)** | *Feasible* | Good VQA and localization support, but operates under Gemma Terms of Use rather than permissive Apache 2.0. |
| **LLaVA-OneVision (7B)** | *Too Heavy* | Exceptional general capability, but 7B parameter footprint requires >20 GB VRAM for fine-tuning, violating student/research team accessibility constraints. |

---

## 4. Multi-Sensor Extension Architecture

While the primary visual backbone consumes calibrated 3-channel optical composites (RGB or false-color NIR composites), the system includes `MultiSensorProjector` in `vqa_captioning/models/multisensor_projector.py`. This enables plug-and-play projection of 12-band Sentinel-2 and 2-band Sentinel-1 SAR embeddings into the LLM token stream, mirroring the RS-InternVL approach from the research paper.
