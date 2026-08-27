# SatQuery AI — Frontend

An Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis (Smart India Hackathon demo frontend).

Built with React + Vite + Tailwind CSS + lucide-react. No backend — all AI responses and analysis results are realistic mock data, structured so a real FastAPI/Python backend can be dropped in later behind the same component props and `src/data/mockData.js` shape.

## Run locally

```bash
npm install
npm run dev
```

Then open the printed local URL (default `http://localhost:5173`).

## Build

```bash
npm run build
npm run preview
```

## Structure

- `src/components` — reusable UI: Sidebar, Header, SatelliteViewer, ImageUploader, ChatPanel, ChatMessage, SuggestedQueries, AnalysisStats, AIInsights, LayerControls, DetectionOverlay, ComparisonViewer, LoadingState.
- `src/pages` — Dashboard, New Analysis, History, Saved, Datasets, Compare, Detection, Land Cover, Change Detection, Settings, Help.
- `src/data/mockData.js` — all mock data and the keyword-based mock AI response engine (`getMockAIResponse`). Replace this file's exports with real API calls to connect a backend.

## Demo flow (SIH judges)

1. **New Analysis** → drag & drop a satellite image.
2. Click **Analyze Image** → simulated AI processing animation.
3. Detected objects, land coverage and AI insights render automatically.
4. In the chat panel, ask *"What can you identify in this image?"* or *"Show me the vegetation areas"* — the matching map layer activates automatically, demonstrating the vision-language link between text and imagery.
