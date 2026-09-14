# BigEarthNet.txt: Dataset Structure, Annotations & Preprocessing Analysis

**Reference**: [arXiv:2603.29630](https://arxiv.org/abs/2603.29630) — *"BigEarthNet.txt: A Large-Scale Multi-Sensor Image-Text Dataset and Benchmark for Earth Observation"*  
**Companion Website**: [txt.bigearth.net](https://txt.bigearth.net)  

---

## 1. Dataset Overview

BigEarthNet.txt is constructed upon the foundational archive of **BigEarthNet v2.0 (reBEN)**. After screening to remove scenes affected by cloud cover, cloud shadows, seasonal snow, and unclassified reference map pixels, the dataset encompasses **464,044 co-registered multi-sensor satellite image pairs** with **9.6 million natural language text annotations**.

### Imaging Sensors
1. **Sentinel-2 Multispectral Instrument (MSI)**:
   - 120 × 120 pixels at 10m Ground Sample Distance (GSD) (1.2 km × 1.2 km spatial footprint).
   - 12 spectral bands: B01–B08, B8A, B09, B11, B12.
   - Natural RGB representation derived from Band 4 (Red), Band 3 (Green), Band 2 (Blue).
2. **Sentinel-1 C-Band Synthetic Aperture Radar (SAR)**:
   - Co-registered dual-polarization: **VV** (vertical transmit / vertical receive) and **VH** (vertical transmit / horizontal receive) backscatter.
   - Preprocessed to dB backscatter representation and standard false-color composites (VV, VH, VV/VH ratio).

---

## 2. Text Annotations & Downstream Tasks

BigEarthNet.txt provides textual annotations across **15 distinct downstream tasks** categorized into 4 core types:

### Category A: Geographically Anchored Captions
Multi-sentence descriptive captions generated via CORINE Land Cover (CLC 2018) reference maps and augmented with Llama-4-Scout-17B paraphrasing and self-refinement:
- Identifies **primary** (>25%), **secondary** (5–25%), and **marginal** (<5%) land-cover classes.
- Specifies pairwise spatial adjacency between classes.
- Grounds context with acquisition season, European country, and Köppen-Geiger climate classification.

### Category B: Binary Yes/No VQA (4 Tasks)
1. `presence`: Verification of whether a land-cover class is visible in the scene.
2. `count`: Verification of the number of distinct contiguous patches of a class (constructed with hard negatives).
3. `size`: Verification of class coverage tier or approximate area.
4. `adjacency`: Spatial proximity verification between two land-cover classes.

### Category C: Multiple-Choice Question (MCQ) VQA (8 Tasks)
Extends the 4 spatial tasks above with relative position, country of acquisition, acquisition season, and Köppen-Geiger climate zone. Each item contains 1 correct answer and 3 semantically plausible distractors.

### Category D: Referring Expression Detection / Grounding (2 Tasks)
1. `referring_lulc_detection`: Textual instruction to localize an instance/class $\rightarrow$ bounding box `[ymin, xmin, ymax, xmax]`.
2. `referring_point_detection`: Centroid point inside target instance $\rightarrow$ enclosing bounding box.

---

## 3. Critical Limitations for SatQuery AI

### Counting Queries
- **Important Finding**: At 10m–20m pixel resolution, CORINE Land Cover annotates **macro land-cover regions**, not discrete physical objects (such as individual buildings, cars, or homes).
- **Semantics**: In BigEarthNet.txt, a "count" represents the **number of contiguous disconnected patches/regions belonging to a land-cover class** (e.g. *"There are 2 distinct patches of coniferous forest"*).
- **SatQuery AI Architecture**: SatQuery-VQA employs `CountEvidenceAdapter`:
  - When users ask land-cover patch count questions, SatQuery-VQA answers directly.
  - When users ask discrete object questions (e.g. *"How many buildings are visible?"*), the system does not hallucinate numbers, but routes the query to the `grounding_change/` module or requests high-resolution imagery.

### Area & Coverage Queries
- BigEarthNet.txt annotations categorize land cover into tiers: Primary (>25%), Secondary (5–25%), and Marginal (<5%), and round areas to the nearest 1,000 m².
- SatQuery-VQA avoids generating ungrounded decimal percentages (e.g. "34.72%"). Exact pixel percentages are calculated dynamically from raster segmentation masks via `AreaCalculator`.

---

## 4. Dataset Splits & Benchmark Split

| Split | Image Pairs | Total Annotations | Description |
|---|---|---|---|
| **Train** | 229,114 | 4,674,281 | Training split for instruction fine-tuning |
| **Validation** | 118,095 | 2,454,690 | Hyperparameter tuning and validation |
| **Test** | 116,835 | 2,424,991 | Unseen test archive |
| **Benchmark Split** | **1,082** | **15,029** | Manually verified, quality-checked gold standard split balanced across answer options and LULC classes. |

---

## 5. Dataset Inspection & Preparation Commands

### Inspect Dataset Directory:
```bash
python vqa_captioning/scripts/run_inspect.py --dataset /path/to/BigEarthNet.txt
```

### Prepare & Validate Unified Splits:
```bash
python vqa_captioning/scripts/run_prepare.py \
    --dataset /path/to/BigEarthNet.txt \
    --output-dir data/prepared_satquery_vqa
```
