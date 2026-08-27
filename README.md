# SatQuery AI

## Project Overview
SatQuery AI is an agentic multimodal AI system for remote-sensing/satellite image analysis. Users will be able to upload optical and SAR satellite imagery, ask natural-language questions, perform VQA, object grounding, change detection, optical-SAR fusion, retrieve remote-sensing knowledge using RAG, and receive evidence-grounded answers with map visualizations and reports.

## Problem Statement / Motivation
Analyzing satellite imagery is often a manual, labor-intensive process requiring specialized geospatial tools. SatQuery AI aims to democratize and automate this process by providing a natural-language interface that leverages state-of-the-art vision-language models, agentic workflows, and geospatial processing to answer complex queries about our planet efficiently and accurately.

## Key Capabilities
- Natural-language satellite image queries
- Optical imagery analysis
- SAR imagery analysis
- Optical-SAR fusion
- VQA
- Image captioning
- Object grounding
- Change detection
- Change-VQA
- Agentic tool orchestration
- RAG
- Geospatial visualization
- Evidence-grounded reports

## High-Level Architecture
The system consists of 6 core modules orchestrated by an Agentic Controller. The controller interprets user intents, interacts with vector databases for knowledge retrieval, and dispatches tasks to specific vision/multimodal modules. The frontend provides a seamless UI, while the backend handles API routing and geospatial processing.

## Repository Structure
```
SatQuery-AI/
├── common/
├── optical_vision/
├── sar_fusion/
├── vqa_captioning/
├── grounding_change/
├── agent_rag/
└── frontend_backend/
```

## Team Ownership
| Person | Folder | Responsibilities |
|---|---|---|
| Person 1 | `optical_vision/` | Optical satellite image preprocessing, ViT/CNN optical encoder, Contrastive pretraining, Optical feature extraction, Training and evaluation, Inference |
| Person 2 | `sar_fusion/` | SAR preprocessing, SAR encoder, Optical-SAR alignment, Cross-attention / multimodal fusion, Fusion training, Evaluation, Inference |
| Person 3 | `vqa_captioning/` | Tokenizer, Text decoder, Multimodal projection, VQA, Captioning, Fine-tuning, Evaluation, Inference |
| Person 4 | `grounding_change/` | Object grounding, Bounding-box prediction, Mask/segmentation support, Change detection, Change-VQA, Training, Evaluation, Inference |
| Person 5 | `agent_rag/` | Agentic controller, Intent/task understanding, Tool dispatcher, Tool/function calling, RAG pipeline, FAISS/vector retrieval, Remote-sensing knowledge corpus, Prompt management, Agent evaluation |
| Person 6 | `frontend_backend/` | React frontend, FastAPI backend, API integration, GDAL/rasterio/geospatial processing, Leaflet/map visualization, Bounding-box and mask overlays, Database, PDF/report generation, Docker/deployment, System integration |

## Datasets
*   **BigEarthNet**: TODO
*   **VRSBench**: TODO
*   **RSVQA**: TODO
*   **CDVQA**: TODO

## Development Workflow
1.  **Pull latest `main`**
2.  **Work in assigned folder** on a feature branch.
3.  **Commit changes**
4.  **Push feature branch**
5.  **Open Pull Request**
6.  **Review**
7.  **Merge into `main`**

**Expected Git Workflow:**
```
main
  │
  ├── feature/optical-vision
  ├── feature/sar-fusion
  ├── feature/vqa-captioning
  ├── feature/grounding-change
  ├── feature/agent-rag
  └── feature/frontend-backend
```
*Note: No direct pushes to main.*

## Git Branching Strategy
Use feature branches off `main` for all development. Follow the `feature/<module-name>-<short-desc>` naming convention.

## Installation / Setup
*TODO: Add installation and setup instructions.*

## Model Training
*TODO: Add model training instructions.*

## Inference
*TODO: Add inference instructions.*

## Evaluation
*TODO: Add evaluation instructions.*

## Docker / Deployment
*TODO: Add Docker deployment instructions.*

## Contribution Guidelines
Please follow the development workflow and branching strategy outlined above. Ensure all changes are well-documented and tested.

## Future Integration Plan
*TODO: Outline the future integration plan across modules.*
