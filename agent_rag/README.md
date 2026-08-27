# Agent & RAG Module

**Owner**: Person 5

**Purpose**:
Acts as the brain of the system, parsing user intents, selecting tools, and retrieving external geospatial knowledge via RAG.

**Responsibilities**:
- Agentic controller
- Intent/task understanding
- Tool dispatcher
- Tool/function calling
- RAG pipeline
- FAISS/vector retrieval
- Remote-sensing knowledge corpus
- Prompt management
- Agent evaluation

**Expected Inputs**:
- Natural language user instructions.

**Expected Outputs**:
- Orchestrated tool calls, augmented prompts, final synthesized answers.

**Planned Models/Components**:
- LLM controller, Vector database (FAISS), Embedding model for text.

**Dataset(s) to be used**:
- Textual geospatial knowledge bases, manuals.

**Training plan**:
- Mostly prompt engineering, potentially tool-use fine-tuning.

**Evaluation metrics**:
- Retrieval precision/recall, tool selection accuracy.

**Inference plan**:
- Multi-step reasoning loop (e.g., ReAct).

**Integration points with other modules**:
- Dispatches tasks to `vqa_captioning`, `grounding_change`. Interfaces with `frontend_backend`.

**Expected API/interface**:
- `process_user_request(query, context)`

**Development checklist**:
- [ ] Setup vector DB (FAISS)
- [ ] Define tool schemas
- [ ] Implement Agentic loop
- [ ] Setup prompt templates
- [ ] Expose integration interface

**TODO**:
- [ ] Define model architecture
- [ ] Add preprocessing pipeline
- [ ] Add training pipeline
- [ ] Add evaluation
- [ ] Add inference
- [ ] Expose integration interface
