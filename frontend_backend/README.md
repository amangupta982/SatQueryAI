# Frontend & Backend Module

**Owner**: Person 6

**Purpose**:
Provides the user interface, APIs, database integration, and geospatial visualization capabilities.

**Responsibilities**:
- React frontend
- FastAPI backend
- API integration
- GDAL/rasterio/geospatial processing
- Leaflet/map visualization
- Bounding-box and mask overlays
- Database
- PDF/report generation
- Docker/deployment
- System integration

**Expected Inputs**:
- User interactions, API requests, outputs from ML modules.

**Expected Outputs**:
- Web interface, API responses, rendered maps, reports.

**Planned Models/Components**:
- React SPA, FastAPI server, PostgreSQL/SQLite database.

**Dataset(s) to be used**:
- N/A

**Training plan**:
- N/A

**Evaluation metrics**:
- Latency, UI responsiveness, API throughput.

**Inference plan**:
- N/A (serves the inference from other modules).

**Integration points with other modules**:
- Wraps all other modules into a cohesive API and UI.

**Expected API/interface**:
- REST/GraphQL endpoints.

**Development checklist**:
- [ ] Setup FastAPI project
- [ ] Setup React project
- [ ] Implement map visualization
- [ ] Implement database models
- [ ] Setup Docker deployment

**TODO**:
- [ ] Define model architecture
- [ ] Add preprocessing pipeline
- [ ] Add training pipeline
- [ ] Add evaluation
- [ ] Add inference
- [ ] Expose integration interface
