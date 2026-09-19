import { useState, useMemo } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft,
  Download,
  Share2,
  RotateCcw,
  Layers,
  Sliders,
  Maximize2,
  CheckCircle2,
  AlertCircle,
  Clock,
  Compass,
  FileDown,
  ChevronDown,
  ChevronRight,
  Eye,
  EyeOff,
  Cpu,
  Boxes,
  GitCompare,
  Radio,
  ExternalLink,
  Info,
  Check,
  Building2,
  Trees,
  Route,
  Droplets,
} from 'lucide-react'
import { structuredAnalysisResults, recentAnalyses } from '../data/mockData'
import DownloadReportButton from '../components/DownloadReportButton'

export default function AnalysisResults() {
  const { analysisId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  // Find result by analysisId, or from location.state, or fallback to default
  const activeResult = useMemo(() => {
    if (analysisId && structuredAnalysisResults[analysisId]) {
      return structuredAnalysisResults[analysisId]
    }
    if (location.state?.result) {
      return location.state.result
    }
    // Default fallback to urban expansion change detection
    return structuredAnalysisResults['urban-expansion-2026']
  }, [analysisId, location.state])

  // View state for Change Analysis: '3-panel' | 'slider' | 'overlay'
  const [changeViewMode, setChangeViewMode] = useState('3-panel')
  const [splitPosition, setSplitPosition] = useState(50)
  const [overlayOpacity, setOverlayOpacity] = useState(65)

  // View state for Object Detection
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true)
  const [confidenceThreshold, setConfidenceThreshold] = useState(85)
  const [selectedCategory, setSelectedCategory] = useState('All')

  // Collapsible Execution Trace
  const [traceExpanded, setTraceExpanded] = useState(false)

  // Notification Toast
  const [toastMsg, setToastMsg] = useState(null)
  const showToast = (msg) => {
    setToastMsg(msg)
    setTimeout(() => setToastMsg(null), 3500)
  }

  // Handle Export Report
  const handleExportReport = () => {
    const reportData = {
      reportType: 'SatQuery Earth Observation Scientific Report',
      analysisId: activeResult.id,
      task: activeResult.task,
      timestamp: activeResult.timestamp,
      model: activeResult.modelName,
      query: activeResult.query,
      metrics: activeResult.metrics || {},
      aiInterpretation: activeResult.interpretation,
      supportingEvidence: activeResult.supportingEvidence || [],
      limitations: activeResult.limitations || null,
      confidence: activeResult.confidence,
      executionTrace: activeResult.executionTrace,
    }
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `SatQuery_Report_${activeResult.id}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    showToast('Scientific report exported as JSON.')
  }

  // Filtered detections for Object Detection view
  const filteredDetections = useMemo(() => {
    if (!activeResult.detections) return []
    return activeResult.detections.filter((det) => {
      const confNum = parseFloat(det.confidence)
      const passesConfidence = confNum >= confidenceThreshold
      const passesCategory = selectedCategory === 'All' || det.category === selectedCategory
      return passesConfidence && passesCategory
    })
  }, [activeResult, confidenceThreshold, selectedCategory])

  return (
    <div className="flex-1 overflow-y-auto bg-[#fafaf8] px-4 py-5 md:px-8 lg:px-12 text-[#162721] selection:bg-[#dce7e1] selection:text-[#162721]">
      <div className="max-w-7xl mx-auto space-y-6 pb-12">
        {/* Floating Toast Notification */}
        {toastMsg && (
          <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-slate-900 text-white text-xs font-medium px-4 py-3 rounded-xl shadow-2xl border border-slate-700 animate-fadeUp">
            <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
            <span>{toastMsg}</span>
          </div>
        )}

        {/* ============================================================ */}
        {/* 1. PROFESSIONAL ANALYSIS HEADER BAR                          */}
        {/* ============================================================ */}
        <div className="bg-white rounded-xl border border-[#e5ebe7] p-4 md:p-5 shadow-sm space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
            {/* Left: Back button & Title */}
            <div className="flex items-start gap-3">
              <button
                onClick={() => navigate('/new-analysis')}
                className="mt-1 p-1.5 rounded-lg border border-[#d8e0dc] text-[#5f7168] hover:text-[#162721] hover:bg-[#f2f6f4] transition-colors"
                title="Back to New Analysis"
              >
                <ArrowLeft size={16} />
              </button>
              <div>
                <div className="flex items-center gap-2.5 flex-wrap">
                  <h1 className="font-display font-bold text-xl md:text-2xl text-[#162721] tracking-tight">
                    {activeResult.title}
                  </h1>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-md bg-[#e2eae5] text-[#234238] border border-[#c8d4ce]">
                    {activeResult.task}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-500 font-mono mt-1 flex-wrap">
                  <span>ID: {activeResult.id}</span>
                  <span>·</span>
                  <span className="flex items-center gap-1">
                    <Clock size={12} />
                    Latency: {activeResult.executionTime}
                  </span>
                  <span>·</span>
                  <span>{activeResult.timestamp}</span>
                </div>
              </div>
            </div>

            {/* Right: Actions */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href)
                  showToast('Workspace URL copied to clipboard.')
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-[#f2f6f4] border border-[#d8e0dc] text-[#234238] rounded-lg text-xs font-semibold shadow-sm transition-all"
              >
                <Share2 size={13} className="text-[#234238]" />
                <span>Share</span>
              </button>

              <DownloadReportButton
                variant="primary"
                reportData={{
                  title: `${activeResult.title} Report`,
                  analysisType: activeResult.task || 'Earth Observation Analysis',
                  query: activeResult.query,
                  modelUsed: activeResult.modelName,
                  prediction: activeResult.interpretation,
                  confidence: activeResult.confidence,
                  sceneDetails: {
                    'Analysis ID': activeResult.id,
                    'Constellation': activeResult.sensor || 'Sentinel Multispectral',
                    'Processing Latency': activeResult.executionTime,
                    'Timestamp': activeResult.timestamp,
                  },
                  statistics: Object.entries(activeResult.metrics || {}).map(([k, v]) => ({
                    label: k.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase()),
                    value: typeof v === 'number' ? (v > 100 ? v.toLocaleString() : v) : String(v),
                  })),
                  evidenceImages: [
                    ...(activeResult.images?.result ? [{ title: 'Analysis Result Layer', src: activeResult.images.result }] : []),
                    ...(activeResult.images?.before ? [{ title: 'Baseline T1 Scene', src: activeResult.images.before }] : []),
                    ...(activeResult.images?.after ? [{ title: 'Post-event T2 Scene', src: activeResult.images.after }] : []),
                  ],
                  limitations: activeResult.limitations || null,
                }}
              />

              <button
                onClick={handleExportReport}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-[#f2f6f4] border border-[#d8e0dc] text-[#234238] rounded-lg text-xs font-semibold shadow-2xs transition-all"
                title="Export raw JSON structured data"
              >
                <Download size={13} className="text-[#234238]" />
                <span>JSON</span>
              </button>

              <button
                onClick={() => navigate('/new-analysis')}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#234238] hover:bg-[#1a342c] text-white rounded-lg text-xs font-semibold shadow-md shadow-[#234238]/20 transition-all"
              >
                <RotateCcw size={13} />
                <span>New Query</span>
              </button>
            </div>
          </div>

          {/* User Question Banner */}
          <div className="p-3 bg-slate-50 border border-slate-200/80 rounded-lg flex items-start gap-2.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 bg-white border border-slate-200 px-1.5 py-0.5 rounded shrink-0 mt-0.5">
              Query
            </span>
            <p className="text-xs font-semibold text-slate-800 leading-relaxed font-body">
              &ldquo;{activeResult.query}&rdquo;
            </p>
          </div>

          {/* Orchestrator Engaged Agents Bar */}
          {location.state?.orchestratorResponse?.agents_used && location.state.orchestratorResponse.agents_used.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap text-xs pt-0.5">
              <span className="text-slate-500 font-medium">Orchestrated Agents:</span>
              {location.state.orchestratorResponse.agents_used.map((agName, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-0.5 rounded-full bg-[#234238]/10 text-[#234238] font-semibold text-[11px] border border-[#234238]/20 flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-[#234238]" />
                  <span>{agName}</span>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* ============================================================ */}
        {/* 2. DEDICATED VISUAL WORKSPACE BY ANALYSIS TYPE               */}
        {/* ============================================================ */}

        {/* CASE A: CHANGE ANALYSIS */}
        {activeResult.task === 'Change Analysis' && (
          <div className="space-y-4">
            {/* View Mode Bar */}
            <div className="bg-white rounded-xl border border-[#e5ebe7] p-2.5 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-lg border border-slate-200/80">
                <button
                  onClick={() => setChangeViewMode('3-panel')}
                  className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                    changeViewMode === '3-panel'
                      ? 'bg-white text-[#234238] shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  3-Panel Grid
                </button>
                <button
                  onClick={() => setChangeViewMode('slider')}
                  className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                    changeViewMode === 'slider'
                      ? 'bg-white text-[#234238] shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Split Slider
                </button>
                <button
                  onClick={() => setChangeViewMode('overlay')}
                  className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                    changeViewMode === 'overlay'
                      ? 'bg-white text-[#234238] shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Change Overlay
                </button>
              </div>

              {/* View options / Slider control */}
              {changeViewMode === 'slider' && (
                <div className="flex items-center gap-2 text-xs font-mono text-slate-500 w-full sm:w-auto">
                  <span>Split: {splitPosition}%</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={splitPosition}
                    onChange={(e) => setSplitPosition(Number(e.target.value))}
                    className="w-36 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#234238]"
                  />
                </div>
              )}

              {changeViewMode === 'overlay' && (
                <div className="flex items-center gap-2 text-xs font-mono text-slate-500 w-full sm:w-auto">
                  <span>Mask Opacity: {overlayOpacity}%</span>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={overlayOpacity}
                    onChange={(e) => setOverlayOpacity(Number(e.target.value))}
                    className="w-36 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-rose-600"
                  />
                </div>
              )}

              {/* Scientific GIS Map Controls (Coordinates HUD & North Arrow) */}
              <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 px-2 py-1 rounded">
                  <Compass size={12} className="text-[#234238]" />
                  <span>North: 0°</span>
                </div>
                <div className="hidden md:block bg-slate-50 border border-slate-200 px-2 py-1 rounded">
                  <span>Scale: 1:25,000 (10m/px)</span>
                </div>
              </div>
            </div>

            {/* Change Analysis Visual Panels */}
            {changeViewMode === '3-panel' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* BEFORE PANEL */}
                <div className="bg-white rounded-xl border border-slate-200/90 overflow-hidden shadow-sm flex flex-col">
                  <div className="px-3.5 py-2 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800">1. BEFORE (T0)</span>
                    <span className="text-[11px] font-mono text-slate-500">
                      {activeResult.beforeImage.date}
                    </span>
                  </div>
                  <div className="relative aspect-[4/3] bg-slate-900 overflow-hidden group">
                    <img
                      src={activeResult.beforeImage.url}
                      alt="Before satellite pass"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute bottom-2 left-2 bg-slate-900/80 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-0.5 rounded">
                      Sentinel-2 L2A · 10m GSD
                    </div>
                  </div>
                </div>

                {/* AFTER PANEL */}
                <div className="bg-white rounded-xl border border-slate-200/90 overflow-hidden shadow-sm flex flex-col">
                  <div className="px-3.5 py-2 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800">2. AFTER (T1)</span>
                    <span className="text-[11px] font-mono text-slate-500">
                      {activeResult.afterImage.date}
                    </span>
                  </div>
                  <div className="relative aspect-[4/3] bg-slate-900 overflow-hidden group">
                    <img
                      src={activeResult.afterImage.url}
                      alt="After satellite pass"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute bottom-2 left-2 bg-slate-900/80 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-0.5 rounded">
                      Sentinel-2 L2A · 10m GSD
                    </div>
                  </div>
                </div>

                {/* CHANGE MAP PANEL */}
                <div className="bg-white rounded-xl border border-rose-200/90 overflow-hidden shadow-sm flex flex-col ring-1 ring-rose-100">
                  <div className="px-3.5 py-2 border-b border-rose-200 bg-rose-50/60 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                      <span className="text-xs font-bold text-rose-900">3. CHANGE MAP</span>
                    </div>
                    <span className="text-[10.5px] font-bold text-rose-700 bg-rose-100/70 border border-rose-200 px-2 py-0.2 rounded-full">
                      Mask Highlighted
                    </span>
                  </div>
                  <div className="relative aspect-[4/3] bg-slate-900 overflow-hidden">
                    <img
                      src={activeResult.afterImage.url}
                      alt="Change map base"
                      className="w-full h-full object-cover filter contrast-125"
                    />
                    {/* SVG Thematic Change Polygon Overlay */}
                    <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                      {/* Urban expansion polygons in semi-transparent red with outline */}
                      <polygon points="35,25 55,20 62,38 48,45 32,35" fill="rgba(225, 29, 72, 0.45)" stroke="#e11d48" strokeWidth="1.2" />
                      <polygon points="58,45 80,40 85,60 65,65" fill="rgba(225, 29, 72, 0.45)" stroke="#e11d48" strokeWidth="1.2" />
                      <polygon points="15,55 30,50 35,70 18,75" fill="rgba(225, 29, 72, 0.45)" stroke="#e11d48" strokeWidth="1.2" />
                      {/* Canopy loss polygon in amber */}
                      <polygon points="40,65 52,62 50,78 38,76" fill="rgba(217, 119, 6, 0.4)" stroke="#d97706" strokeWidth="1.2" />
                    </svg>

                    <div className="absolute top-2 right-2 bg-slate-900/85 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-1 rounded border border-slate-700 space-y-0.5">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded bg-rose-500" />
                        <span>Built-up (+13.4%)</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded bg-amber-500" />
                        <span>Canopy (-4.8 km²)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* SPLIT SLIDER VIEW */}
            {changeViewMode === 'slider' && (
              <div className="bg-white rounded-xl border border-slate-200/90 p-2 shadow-sm">
                <div className="relative h-[420px] md:h-[480px] rounded-lg overflow-hidden select-none">
                  {/* Base After Image */}
                  <img
                    src={activeResult.afterImage.url}
                    alt="After pass"
                    className="absolute inset-0 w-full h-full object-cover"
                  />
                  <div className="absolute top-3 right-3 bg-slate-900/80 text-white text-xs font-mono px-2.5 py-1 rounded shadow-md z-10">
                    AFTER: {activeResult.afterImage.date}
                  </div>

                  {/* Clipped Before Image */}
                  <div
                    className="absolute inset-0 overflow-hidden"
                    style={{ width: `${splitPosition}%` }}
                  >
                    <img
                      src={activeResult.beforeImage.url}
                      alt="Before pass"
                      className="absolute inset-0 w-full h-full object-cover max-w-none"
                      style={{ width: '100%', height: '100%' }}
                    />
                    <div className="absolute top-3 left-3 bg-slate-900/80 text-white text-xs font-mono px-2.5 py-1 rounded shadow-md">
                      BEFORE: {activeResult.beforeImage.date}
                    </div>
                  </div>

                  {/* Divider Line */}
                  <div
                    className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_12px_rgba(0,0,0,0.6)] z-20 pointer-events-none"
                    style={{ left: `${splitPosition}%` }}
                  >
                    <div className="absolute top-1/2 -translate-y-1/2 -left-3.5 w-8 h-8 rounded-full bg-white border border-slate-300 shadow-lg flex items-center justify-center text-slate-700 text-xs font-bold font-mono">
                      ⇄
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* OVERLAY VIEW */}
            {changeViewMode === 'overlay' && (
              <div className="bg-white rounded-xl border border-slate-200/90 p-2 shadow-sm">
                <div className="relative h-[420px] md:h-[480px] rounded-lg overflow-hidden select-none bg-slate-900">
                  <img
                    src={activeResult.afterImage.url}
                    alt="After satellite scene"
                    className="w-full h-full object-cover"
                  />
                  <svg
                    className="absolute inset-0 w-full h-full pointer-events-none"
                    viewBox="0 0 100 100"
                    preserveAspectRatio="none"
                    style={{ opacity: overlayOpacity / 100 }}
                  >
                    <polygon points="35,25 55,20 62,38 48,45 32,35" fill="#e11d48" stroke="#ffffff" strokeWidth="0.8" />
                    <polygon points="58,45 80,40 85,60 65,65" fill="#e11d48" stroke="#ffffff" strokeWidth="0.8" />
                    <polygon points="15,55 30,50 35,70 18,75" fill="#e11d48" stroke="#ffffff" strokeWidth="0.8" />
                    <polygon points="40,65 52,62 50,78 38,76" fill="#d97706" stroke="#ffffff" strokeWidth="0.8" />
                  </svg>
                  <div className="absolute bottom-3 left-3 bg-slate-900/80 backdrop-blur-xs text-white text-xs font-mono px-3 py-1.5 rounded space-y-1">
                    <p className="font-semibold text-rose-300">Bi-Temporal Change Delineation Mask</p>
                    <p className="text-[11px] text-slate-300">Red: New Built-up · Amber: Canopy Deficit</p>
                  </div>
                </div>
              </div>
            )}

            {/* Metrics Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {activeResult.metrics.map((m, idx) => (
                <div key={idx} className="bg-white rounded-xl border border-slate-200/90 p-3.5 shadow-sm">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    {m.label}
                  </span>
                  <p className="text-xl font-bold text-slate-900 tracking-tight font-display mt-1">
                    {m.value}
                  </p>
                  <span className="text-[11px] text-slate-500 mt-0.5 block">{m.detail}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CASE B: OBJECT DETECTION / GROUNDING */}
        {activeResult.task === 'Object Detection' && (
          <div className="space-y-4">
            {/* Controls Bar */}
            <div className="bg-white rounded-xl border border-[#e5ebe7] p-3 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
              {/* Category Pills */}
              <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
                <button
                  onClick={() => setSelectedCategory('All')}
                  className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                    selectedCategory === 'All'
                      ? 'bg-[#234238] text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-[#f2f6f4]'
                  }`}
                >
                  All ({activeResult.objectsDetectedCount})
                </button>
                {activeResult.categories?.map((cat) => (
                  <button
                    key={cat.name}
                    onClick={() => setSelectedCategory(cat.name)}
                    className={`px-2.5 py-1 text-xs font-medium rounded-lg transition-all whitespace-nowrap flex items-center gap-1.5 ${
                      selectedCategory === cat.name
                        ? 'bg-[#234238] text-white shadow-sm'
                        : 'bg-slate-100 text-slate-600 hover:bg-[#f2f6f4]'
                    }`}
                  >
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cat.color }} />
                    <span>{cat.name}</span>
                    <span className="font-mono text-[10px] opacity-80">({cat.count})</span>
                  </button>
                ))}
              </div>

              {/* Toggles & Threshold Slider */}
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-slate-500 font-mono">Confidence: ≥ {confidenceThreshold}%</span>
                  <input
                    type="range"
                    min="50"
                    max="98"
                    value={confidenceThreshold}
                    onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                    className="w-28 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#234238]"
                  />
                </div>

                <button
                  onClick={() => setShowBoundingBoxes(!showBoundingBoxes)}
                  className={`px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                    showBoundingBoxes
                      ? 'bg-[#e2eae5] border-[#c8d4ce] text-[#234238]'
                      : 'bg-white border-[#d8e0dc] text-slate-600'
                  }`}
                >
                  {showBoundingBoxes ? <Eye size={13} /> : <EyeOff size={13} />}
                  <span>{showBoundingBoxes ? 'Boxes Visible' : 'Boxes Hidden'}</span>
                </button>
              </div>
            </div>

            {/* High-Resolution Imagery Viewer with Bounding Boxes */}
            <div className="bg-white rounded-xl border border-[#e5ebe7] p-2 shadow-sm">
              <div className="relative h-[440px] md:h-[500px] rounded-lg overflow-hidden select-none bg-slate-950">
                <img
                  src={activeResult.mainImage?.url}
                  alt="High resolution satellite scene"
                  className="w-full h-full object-cover"
                />

                {/* Render Bounding Boxes Overlay */}
                {showBoundingBoxes && (
                  <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                    {filteredDetections.map((det) => {
                      const [x, y, w, h] = det.bbox
                      return (
                        <g key={det.id}>
                          <rect
                            x={x}
                            y={y}
                            width={w}
                            height={h}
                            fill="rgba(35, 66, 56, 0.2)"
                            stroke="#234238"
                            strokeWidth="0.8"
                            rx="1"
                          />
                        </g>
                      )
                    })}
                  </svg>
                )}

                {/* HTML Labels over image */}
                {showBoundingBoxes &&
                  filteredDetections.map((det) => {
                    const [x, y] = det.bbox
                    return (
                      <div
                        key={det.id}
                        className="absolute pointer-events-none text-[10px] font-mono bg-[#234238] text-white px-1.5 py-0.2 rounded shadow-sm"
                        style={{ left: `${x}%`, top: `${Math.max(0, y - 4)}%` }}
                      >
                        {det.label} ({det.confidence})
                      </div>
                    )
                  })}

                {/* Bottom HUD bar */}
                <div className="absolute bottom-3 left-3 bg-slate-900/85 backdrop-blur-xs text-white text-xs font-mono px-3 py-1.5 rounded border border-slate-700 flex items-center gap-3">
                  <span>Cartosat-3 Optical (0.28m PAN)</span>
                  <span>·</span>
                  <span>Visible Objects: {filteredDetections.length}</span>
                </div>
              </div>
            </div>

            {/* Detections Data Table */}
            <div className="bg-white rounded-xl border border-[#e5ebe7] p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Delineated Objects & Spatial Coordinates
                </h3>
                <span className="text-xs font-mono text-slate-400">
                  Showing {filteredDetections.length} of {activeResult.detections?.length || 0}
                </span>
              </div>

              <div className="overflow-x-auto rounded-lg border border-slate-200">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 text-[11px]">
                    <tr>
                      <th className="py-2 px-3">Object Label</th>
                      <th className="py-2 px-3">Category</th>
                      <th className="py-2 px-3">Model Confidence</th>
                      <th className="py-2 px-3">Geographic Coordinates</th>
                      <th className="py-2 px-3">Bounding Box (X, Y, W, H)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {filteredDetections.map((det) => (
                      <tr key={det.id} className="hover:bg-slate-50/60">
                        <td className="py-2 px-3 font-semibold text-slate-900">{det.label}</td>
                        <td className="py-2 px-3">
                          <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700">
                            {det.category}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-[#234238] font-semibold">{det.confidence}</td>
                        <td className="py-2 px-3 text-slate-500">{det.coordinates}</td>
                        <td className="py-2 px-3 text-slate-400">
                          [{det.bbox.join(', ')}]
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* CASE C: OPTICAL + SAR MULTIMODAL ANALYSIS */}
        {activeResult.task === 'Optical + SAR' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Optical Panel */}
              <div className="bg-white rounded-xl border border-slate-200/90 overflow-hidden shadow-sm flex flex-col">
                <div className="px-3.5 py-2 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800">1. OPTICAL REFLECTANCE</span>
                  <span className="text-[11px] font-mono text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.2 rounded">
                    {activeResult.opticalImage?.cloudCover}
                  </span>
                </div>
                <div className="relative aspect-[4/3] bg-slate-900 overflow-hidden">
                  <img
                    src={activeResult.opticalImage?.url}
                    alt="Optical pass"
                    className="w-full h-full object-cover filter brightness-95"
                  />
                  <div className="absolute bottom-2 left-2 bg-slate-900/80 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-0.5 rounded">
                    Sentinel-2 L2A · Optical RGB
                  </div>
                </div>
              </div>

              {/* SAR Panel - Authentic Radar Styling */}
              <div className="bg-white rounded-xl border border-slate-200/90 overflow-hidden shadow-sm flex flex-col">
                <div className="px-3.5 py-2 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800">2. SAR MICROWAVE BACKSCATTER</span>
                  <span className="text-[11px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.2 rounded">
                    Cloud Penetrated
                  </span>
                </div>
                <div className="relative aspect-[4/3] bg-slate-950 overflow-hidden">
                  {/* Grayscale high-contrast filter to resemble authentic C-Band SAR radar backscatter */}
                  <img
                    src={activeResult.sarImage?.url}
                    alt="SAR pass"
                    className="w-full h-full object-cover filter grayscale contrast-200 brightness-90"
                  />
                  <div className="absolute bottom-2 left-2 bg-slate-900/85 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-0.5 rounded border border-slate-700">
                    RISAT-1A SAR · 5.35 GHz C-Band (HH/HV)
                  </div>
                </div>
              </div>

              {/* Fused Multimodal Inundation Panel */}
              <div className="bg-white rounded-xl border border-blue-300 overflow-hidden shadow-sm flex flex-col ring-1 ring-blue-100">
                <div className="px-3.5 py-2 border-b border-blue-200 bg-blue-50/70 flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
                    <span className="text-xs font-bold text-blue-900">3. FUSED INUNDATION MASK</span>
                  </div>
                  <span className="text-[10.5px] font-bold text-blue-700 bg-blue-100/80 border border-blue-200 px-2 py-0.2 rounded-full">
                    Flood Extent
                  </span>
                </div>
                <div className="relative aspect-[4/3] bg-slate-900 overflow-hidden">
                  <img
                    src={activeResult.fusedImage?.url}
                    alt="Fused flood map"
                    className="w-full h-full object-cover filter contrast-125"
                  />
                  {/* SVG flood water mask overlay */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <polygon points="20,30 45,28 65,45 50,68 25,60" fill="rgba(37, 99, 235, 0.55)" stroke="#3b82f6" strokeWidth="1.2" />
                    <polygon points="60,15 85,18 80,45 62,35" fill="rgba(37, 99, 235, 0.55)" stroke="#3b82f6" strokeWidth="1.2" />
                  </svg>
                  <div className="absolute top-2 right-2 bg-slate-900/85 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-1 rounded border border-slate-700">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded bg-blue-500" />
                      <span>Flood Inundation (115.6 km²)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Metrics Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {activeResult.metrics?.map((m, idx) => (
                <div key={idx} className="bg-white rounded-xl border border-slate-200/90 p-3.5 shadow-sm">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    {m.label}
                  </span>
                  <p className="text-xl font-bold text-slate-900 tracking-tight font-display mt-1">
                    {m.value}
                  </p>
                  <span className="text-[11px] text-slate-500 mt-0.5 block">{m.detail}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CASE D: VISUAL QUESTION ANSWERING (VQA) */}
        {activeResult.task === 'Visual Question Answering' && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-slate-200/90 p-2 shadow-sm">
              <div className="relative h-[420px] md:h-[480px] rounded-lg overflow-hidden select-none bg-slate-950">
                <img
                  src={activeResult.mainImage?.url}
                  alt="VQA Scene"
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-3 left-3 bg-slate-900/85 backdrop-blur-xs text-white text-xs font-mono px-3 py-1.5 rounded border border-slate-700">
                  Sentinel-2 L2A Multispectral · Band 4/3/2 + NIR
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ============================================================ */}
        {/* 3. SCIENTIFIC AI INTERPRETATION & EVIDENCE SECTION           */}
        {/* ============================================================ */}
        <div className="bg-white rounded-xl border border-[#e5ebe7] p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="font-display font-bold text-base text-[#162721] flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#234238]" />
              <span>Scientific AI Interpretation</span>
            </h2>

            {/* Model Confidence Tag - Explicit Handling */}
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-slate-400">Confidence:</span>
              <span
                className={`font-semibold px-2 py-0.5 rounded ${
                  activeResult.confidence === 'Confidence not provided by model'
                    ? 'bg-slate-100 text-slate-500 border border-slate-200'
                    : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                }`}
              >
                {activeResult.confidence}
              </span>
            </div>
          </div>

          {/* Actual Interpretation Text */}
          <div className="prose prose-slate max-w-none">
            <p className="text-sm text-slate-800 leading-relaxed font-body">
              {activeResult.interpretation}
            </p>
          </div>

          {/* Supporting Evidence Bullets */}
          {activeResult.supportingEvidence && (
            <div className="pt-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                Observational Evidence & Spectral Markers (Image Evidence)
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-700">
                {activeResult.supportingEvidence.map((ev, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <Check size={14} className="text-emerald-500 shrink-0 mt-0.5" />
                    <span>{ev}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Domain Knowledge Evidence (RAG) strictly partitioned from Image Evidence */}
          {location.state?.orchestratorResponse?.knowledge_evidence && location.state.orchestratorResponse.knowledge_evidence.length > 0 && (
            <div className="pt-3 border-t border-slate-100">
              <h4 className="text-xs font-bold uppercase tracking-wider text-sky-800 mb-2 flex items-center gap-1.5">
                <span>Domain Knowledge & Literature Evidence (RAG)</span>
              </h4>
              <div className="space-y-2">
                {location.state.orchestratorResponse.knowledge_evidence.map((k, i) => (
                  <div key={i} className="p-3 bg-sky-50/60 border border-sky-200/70 rounded-lg text-xs">
                    <div className="flex items-center justify-between font-mono text-[10.5px] text-sky-900 font-bold mb-1">
                      <span>Source: {k.source}</span>
                      {k.section && <span>Topic: {k.section}</span>}
                    </div>
                    <p className="text-slate-700 leading-relaxed font-body">{k.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Limitations & Uncertainty Note */}
          {activeResult.limitations && (
            <div className="p-3 bg-amber-50/60 border border-amber-200/70 rounded-lg text-xs text-amber-900 flex items-start gap-2">
              <Info size={14} className="text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Sensor & Atmospheric Limitations: </span>
                <span>{activeResult.limitations}</span>
              </div>
            </div>
          )}

          {/* Output Artifacts Download Row */}
          {activeResult.evidenceArtifacts && (
            <div className="pt-2 border-t border-slate-100 flex items-center gap-2 flex-wrap text-xs">
              <span className="text-slate-400 font-medium">Generated Artifacts:</span>
              {activeResult.evidenceArtifacts.map((art, i) => (
                <button
                  key={i}
                  onClick={() => showToast(`Downloading ${art.name}...`)}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 font-mono text-[11px] transition-colors"
                >
                  <FileDown size={12} className="text-slate-500" />
                  <span>{art.name}</span>
                  <span className="text-slate-400">({art.size})</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* ============================================================ */}
        {/* 4. EXECUTION TRACE ACCORDION (COLLAPSIBLE)                    */}
        {/* ============================================================ */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
          <button
            onClick={() => setTraceExpanded(!traceExpanded)}
            className="w-full px-5 py-3.5 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
              <Cpu size={14} className="text-slate-500" />
              <span>How this result was produced</span>
              <span className="text-[11px] font-mono text-slate-400">
                ({activeResult.executionTrace?.requestId || 'Execution Profile'})
              </span>
            </div>

            <div className="flex items-center gap-2 text-slate-400">
              <span className="text-xs">{traceExpanded ? 'Collapse' : 'Expand Trace'}</span>
              {traceExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </div>
          </button>

          {traceExpanded && activeResult.executionTrace && (
            <div className="px-5 pb-5 pt-2 border-t border-slate-100 space-y-4 text-xs font-mono bg-slate-50/50">
              {/* Pipeline Stage Checkpoints */}
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2 font-sans">
                  Pipeline Stage Checkpoints
                </span>
                <div className="space-y-1.5 bg-white p-3 rounded-lg border border-slate-200">
                  {activeResult.executionTrace.pipelineStages?.map((st, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={13} className="text-emerald-500" />
                        <span className="text-slate-700">{st.name}</span>
                      </div>
                      <span className="text-slate-400">{st.duration}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Hardware & Compute Environment */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11.5px]">
                <div className="p-3 bg-slate-900 text-slate-200 rounded-lg space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-sans block mb-1">
                    Model Infrastructure
                  </span>
                  <div>
                    <span className="text-slate-400">Model Checkpoint: </span>
                    <span className="text-emerald-400">{activeResult.executionTrace.modelCheckpoint}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Cluster Node: </span>
                    <span className="text-sky-300">{activeResult.executionTrace.gpuNode}</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-900 text-slate-200 rounded-lg space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-sans block mb-1">
                    Input Telemetry
                  </span>
                  <div>
                    <span className="text-slate-400">Sensor Bands: </span>
                    <span className="text-amber-300">{activeResult.executionTrace.sensorBands}</span>
                  </div>
                  <div className="truncate">
                    <span className="text-slate-400">Input Scenes: </span>
                    <span className="text-slate-300">
                      {activeResult.executionTrace.inputScenes?.join(', ')}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
