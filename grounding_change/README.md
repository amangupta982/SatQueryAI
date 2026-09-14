# Grounding & Change Intelligence Module (`grounding_change`)

**Owner**: Person 4 (Spatial Understanding & Multitemporal Change Intelligence)

**Purpose**:
Performs comprehensive multitemporal satellite and aerial change intelligence, visual grounding (bounding boxes and masks), semantic land-cover transition tracking, and interactive multi-turn visual question answering (VQA).

Unlike a simple binary change detector, for every pair of temporal images (T1 earlier, T2 later), this module constructs a **Complete Change Representation** of the scene across all detectable land-cover categories, and enables the SatQueryAI agent to interactively query, filter, rank, localize, and explain any aspect of the detected changes.

---

## 🚀 Key System Capabilities

1. **Zero-Question Initial Scene Analysis**:
   - Accepts $T_1 + T_2$ without requiring any user question.
   - Generates a complete inventory of changes across all 7 standard categories (buildings, vegetation, water, bare land, infrastructure, etc.).
   - Computes quantitative statistics (area deltas, region distributions, physical area in $\text{m}^2$ and hectares).
   - Generates a continuous change intensity heatmap and multi-layer visual evidence.
   - Formulates an executive natural-language summary.

2. **Multitemporal Land-Cover Transitions**:
   - Detects explicit from $\rightarrow$ to transitions (e.g. `vegetation -> building` [conversion], `bare_land -> building` [addition], `vegetation -> bare_land` [clearing]).

3. **Discrete Spatial Grounding & Geospatial Localization**:
   - Connected-components extraction with pixel bounding boxes, centroids, and RLE masks.
   - Converts image pixel locations to projected coordinates (UTM/WebMercator) and WGS84 Latitude/Longitude using CRS and affine transforms.
   - Never fabricates real-world coordinates when geospatial metadata is missing.
   - One-click RFC 7946 GeoJSON export.

4. **Continuous Change Heatmap & Multi-Scale Evidence**:
   - Generates composite continuous change intensity maps combining neural difference features, learned probability, and semantic shifts.
   - Multi-layer visual rendering with toggleable category overlays, bounding boxes, centroid pins, and machine-readable legend metadata.

5. **Interactive Session Memory & Agent Reasoning**:
   - Caches the complete `TemporalChangeScene` in memory with TTL.
   - Follow-up conversational queries (`"Where?"`, `"Give coordinates"`, `"Only buildings"`, `"Show largest"`, `"Show everything again"`) execute directly over the stored scene without re-running heavy visual models.

---

## 📊 Dataset Strategy & Priority

The module follows a multi-dataset strategy combining interactive bitemporal VQA, dense semantic change detection, and visual grounding:

| Priority | Dataset | Focus / Task | Source |
|:---|:---|:---|:---|
| **1 (Primary)** | **ChangeChat-105k** | Multi-turn conversational bitemporal VQA | HuggingFace: `hlwu/changechat-105k` + LEVIR-CC |
| **2** | **RSRCC** | Regional change question answering | Google Research / HuggingFace: `google/RSRCC` |
| **3** | **QAG-360K (VisTA)** | Change grounding masks & boxes | `https://github.com/like413/VisTA` |
| **4** | **SECOND** | 6-class semantic change detection | Wuhan University |
| **5 (Optional)** | **BigEarthNet.txt** | Multimodal multispectral scene VQA | `arXiv:2603.29630` |
| **6 (Optional)** | **RSVLM-QA** | High-resolution aerial grounding & QA | `arXiv:2508.07918` |

---

## 🛠️ CLI Quickstart

### 1. Dataset Management
```bash
# Check dataset readiness status
python -m grounding_change.data.download_datasets --report

# Download specific dataset or profile
python -m grounding_change.data.download_datasets --profile minimal
python -m grounding_change.data.download_datasets --dataset changechat
```

### 2. Model Training
```bash
# Verify pre-training prerequisites
python -m grounding_change.training.train --precheck

# Train with specific profile
python -m grounding_change.training.train --profile minimal --epochs 10 --batch-size 4
python -m grounding_change.training.train --profile full
python -m grounding_change.training.train --profile vqa
python -m grounding_change.training.train --profile change
python -m grounding_change.training.train --profile grounding
```

### 3. Evaluation & Benchmarking
```bash
# Quantitative benchmark metrics (Precision, Recall, F1, mIoU, Box IoU, VQA)
python -m grounding_change.evaluation.evaluate --task all --output outputs/eval.json

# Generate 6-panel qualitative evaluation strips (T1 | T2 | Diff | Change | Semantic | Grounding)
python -m grounding_change.evaluation.evaluate --qualitative
```

### 4. Running Test Suites
```bash
# Run all unit and smoke tests
python -m pytest grounding_change/tests/ --basetemp=outputs/pytest_temp -v
```

---

## 💻 Agent Tool Python API

```python
from grounding_change.inference import (
    analyze_temporal_scene,
    query_temporal_scene,
    filter_changes,
    rank_changes,
    get_region,
    export_geojson
)

# 1. Zero-question scene analysis
output = analyze_temporal_scene(
    image_t1="path/to/t1.tif",
    image_t2="path/to/t2.tif",
    metadata={"crs": "EPSG:4326", "transform": [0.001, 0, 77.5, 0, -0.001, 13.0]},
    session_id="session_01"
)

print(output.answer)
print(f"Total scene change: {output.scene_summary.change_percentage}%")

# 2. Interactive follow-up queries (reuses stored session)
res1 = query_temporal_scene("session_01", "Where are the new buildings?")
res2 = query_temporal_scene("session_01", "Give me latitude and longitude.")
res3 = query_temporal_scene("session_01", "Show me everything again.")

# 3. Export to GeoJSON
geojson_fc = export_geojson("session_01", output_path="outputs/changes.geojson")
```

---

## 🌐 Frontend & API Integration

- **FastAPI Endpoints**:
  - `POST /api/v1/change-analysis/analyze`: Initial bitemporal analysis
  - `POST /api/v1/change-analysis/query`: Interactive session follow-up questions
  - `POST /api/v1/change-analysis/filter`: Spatial filtering
  - `GET /api/v1/change-analysis/session/{id}`: Cached scene inspection
  - `GET /api/v1/change-analysis/session/{id}/geojson`: GeoJSON export
  - `GET /api/v1/change-analysis/evidence/{filename}`: Evidence layer delivery
- **React Frontend**:
  - Accessible via `/change-analysis` and the "Change Intelligence" navigation link in the top bar.
  - Synchronized dual-temporal viewer with linked zoom/pan and split slider mode.
  - Interactive SVG bounding box selection and centroid inspection.
  - Layer toggles, category filters, statistics dashboard, and embedded multi-turn VQA chat.
