# SatQuery AI Project Overview & Architectural Guidelines

## Mission and Architecture
SatQuery AI is an agentic multimodal artificial intelligence system engineered specifically for remote sensing, satellite earth observation, and geospatial analytics.

## Core Specialist Modules
SatQuery AI orchestrates distinct specialist capabilities:
1. **SatQuery-VQA (Visual Question Answering)**: Dual-stream Convolutional Vision Backbone + GRU text encoder + Cross-Attention Multimodal Fusion for high-resolution satellite imagery inspection.
2. **Geospatial Area Measurement & Object Grounding**: Delivers precise polygon delineation, geometric bounding boxes $[x_{\min}, y_{\min}, x_{\max}, y_{\max}]$, and hectare/square-kilometer polygon measurements.
3. **Change Intelligence**: Bi-temporal Siamese difference networks computing land transformation metrics, deforestation indices, and urban expansion heatmaps.
4. **Optical-SAR Agent**: Multimodal fusion reconciling Sentinel-1 (C-band SAR) with Sentinel-2 / Cartosat optical scenes.
5. **RAG / Remote Sensing Knowledge**: Specialized domain-knowledge retrieval augmented generation grounded in scientific remote sensing documentation, ISRO literature, and benchmark definitions.

## Key Operational Principle: Separation of Concerns
- **Specialist Vision Models**: Handle direct image analysis (e.g., "How many buildings are in this image?", "What changed between these two images?", "Find all roads in this image").
- **RAG Knowledge Pipeline**: Handles domain science questions (e.g., "What is SAR?", "What is NDVI?", "Why combine optical and SAR?", "Explain BigEarthNet.txt"). The RAG knowledge pipeline operates strictly on indexed domain literature and distinguishes knowledge evidence from direct satellite image evidence.
