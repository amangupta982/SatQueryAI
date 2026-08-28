import { useState } from 'react'
import ImageUploader from '../components/ImageUploader'
import SatelliteViewer from '../components/SatelliteViewer'
import ChatPanel from '../components/ChatPanel'
import AnalysisStats from '../components/AnalysisStats'
import LoadingState from '../components/LoadingState'
import {
  CheckCircle2,
  GitCompare,
  Layers,
  ArrowRightLeft,
  Calendar,
  Building2,
  Trees,
  Route,
  RotateCcw,
  SlidersHorizontal,
} from 'lucide-react'
import { activeImage } from '../data/mockData'

export default function NewAnalysis() {
  const [stage, setStage] = useState('upload') // upload -> processing -> results
  const [isCompareMode, setIsCompareMode] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [layers, setLayers] = useState(['satellite', 'detection'])
  const [compareSplit, setCompareSplit] = useState(50)
  const [compareViewType, setCompareViewType] = useState('slider') // 'slider' | 'side-by-side'
  const [activeImageIndex, setActiveImageIndex] = useState(0)

  const toggleLayer = (key) => {
    setLayers((prev) => (prev.includes(key) ? prev.filter((l) => l !== key) : [...prev, key]))
  }

  const activateFromChat = (key) => {
    setLayers((prev) => (prev.includes(key) ? prev : [...prev, key]))
  }

  const handleAnalyze = (files, compareModeRequested) => {
    setUploadedFiles(files || [])
    if (compareModeRequested || (files && files.length >= 2)) {
      setIsCompareMode(true)
    }
    setStage('processing')
    setTimeout(() => setStage('results'), 1900)
  }

  const resetAnalysis = () => {
    setStage('upload')
    setUploadedFiles([])
  }

  const currentPreview = uploadedFiles[activeImageIndex]?.preview || activeImage.thumbnail
  const comparePreviewA = uploadedFiles[0]?.preview || activeImage.thumbnail
  const comparePreviewB = uploadedFiles[1]?.preview || activeImage.thumbnail

  return (
    <div className="flex-1 min-h-0 flex overflow-hidden p-4 lg:p-4 gap-4 bg-[#f8f9fb]">
      <div className="flex-1 min-w-0 overflow-y-auto space-y-4 pr-1">
        {/* Stage 1: Upload Stage */}
        {stage === 'upload' && (
          <div className="max-w-2xl mx-auto mt-4 space-y-4">
            <ImageUploader
              onAnalyze={handleAnalyze}
              isCompareMode={isCompareMode}
              onToggleCompareMode={() => setIsCompareMode((v) => !v)}
            />

            {/* 3 Step indicators */}
            <div className="grid grid-cols-3 gap-3 text-center">
              <StepChip n={1} label="Upload" active />
              <StepChip n={2} label="Analyze" />
              <StepChip n={3} label="Explore" />
            </div>

            {/* Compare Button below the upload / analyze / explore buttons */}
            <button
              onClick={() => setIsCompareMode((v) => !v)}
              className={`w-full flex items-center justify-between p-3.5 rounded-2xl border transition-all shadow-xs ${
                isCompareMode
                  ? 'border-blue-500 bg-blue-50/70 ring-2 ring-blue-100'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/80'
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                    isCompareMode ? 'bg-blue-600 text-white' : 'bg-blue-50 text-blue-600'
                  }`}
                >
                  <GitCompare size={17} strokeWidth={2} />
                </div>
                <div className="text-left">
                  <p className="text-xs font-bold text-slate-900">
                    {isCompareMode ? 'Comparison Mode Active' : 'Compare Multiple Images'}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {isCompareMode
                      ? 'Upload 2+ imagery passes to perform bi-temporal change detection'
                      : 'Click to enable multi-scene comparison & temporal change detection'}
                  </p>
                </div>
              </div>

              <span
                className={`text-xs font-semibold px-3 py-1 rounded-lg border ${
                  isCompareMode
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-slate-100 text-slate-700 border-slate-200'
                }`}
              >
                {isCompareMode ? 'Enabled ✓' : 'Enable Compare'}
              </span>
            </button>
          </div>
        )}

        {/* Stage 2: Processing Stage */}
        {stage === 'processing' && (
          <div className="max-w-2xl mx-auto mt-10">
            <LoadingState />
          </div>
        )}

        {/* Stage 3: Results Stage */}
        {stage === 'results' && (
          <div className="space-y-4 animate-fadeUp">
            {/* Top Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-xs">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
                  <CheckCircle2 size={14} />
                  <span>
                    {isCompareMode
                      ? 'Comparison & Change Detection Complete'
                      : `Analysis Complete — ${uploadedFiles.length || 1} Scene Loaded`}
                  </span>
                </div>

                {uploadedFiles.length > 1 && (
                  <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
                    {uploadedFiles.map((f, idx) => (
                      <button
                        key={f.id}
                        onClick={() => setActiveImageIndex(idx)}
                        className={`text-xs px-2.5 py-1 rounded-lg font-medium transition-colors ${
                          activeImageIndex === idx
                            ? 'bg-white text-slate-900 shadow-xs font-semibold'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        Image {idx + 1}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={resetAnalysis}
                className="flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl hover:bg-slate-100 transition-colors"
              >
                <RotateCcw size={13} />
                <span>New Analysis</span>
              </button>
            </div>

            {/* If in Compare Mode: Interactive Comparison & Change Detection */}
            {isCompareMode ? (
              <div className="space-y-4">
                {/* Comparison Viewer Card */}
                <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                        <GitCompare size={16} />
                      </div>
                      <div>
                        <h3 className="text-xs font-bold text-slate-900">Bi-Temporal Scene Comparison</h3>
                        <p className="text-[11px] text-slate-500">Cartosat-3 Pass A vs Pass B (Change Detection)</p>
                      </div>
                    </div>

                    {/* View Type Toggle */}
                    <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
                      <button
                        onClick={() => setCompareViewType('slider')}
                        className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors ${
                          compareViewType === 'slider'
                            ? 'bg-white text-blue-600 shadow-xs font-semibold'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        Split Slider
                      </button>
                      <button
                        onClick={() => setCompareViewType('side-by-side')}
                        className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors ${
                          compareViewType === 'side-by-side'
                            ? 'bg-white text-blue-600 shadow-xs font-semibold'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        Side-by-Side
                      </button>
                    </div>
                  </div>

                  {/* Viewer Display */}
                  {compareViewType === 'slider' ? (
                    <div className="relative h-[380px] lg:h-[420px] rounded-xl overflow-hidden border border-slate-200 select-none">
                      {/* Base Image (Pass B - After) */}
                      <img
                        src={comparePreviewB}
                        alt="Pass B"
                        className="absolute inset-0 w-full h-full object-cover filter contrast-105"
                      />
                      <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm border border-slate-200 rounded-lg px-2.5 py-1 text-[11px] font-semibold text-slate-800 z-10 shadow-xs">
                        Pass B (2026)
                      </div>

                      {/* Clipped Overlay (Pass A - Before) */}
                      <div
                        className="absolute inset-0 overflow-hidden"
                        style={{ width: `${compareSplit}%` }}
                      >
                        <img
                          src={comparePreviewA}
                          alt="Pass A"
                          className="absolute inset-0 w-full h-full object-cover max-w-none"
                          style={{ width: '100%', height: '100%' }}
                        />
                        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm border border-slate-200 rounded-lg px-2.5 py-1 text-[11px] font-semibold text-slate-800 shadow-xs">
                          Pass A (2024)
                        </div>
                      </div>

                      {/* Split Divider Bar */}
                      <div
                        className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_10px_rgba(0,0,0,0.4)] pointer-events-none z-20"
                        style={{ left: `${compareSplit}%` }}
                      >
                        <div className="absolute top-1/2 -translate-y-1/2 -left-3.5 w-8 h-8 rounded-full bg-white border border-slate-300 shadow-md flex items-center justify-center text-slate-700">
                          <ArrowRightLeft size={13} />
                        </div>
                      </div>

                      {/* Split Control Slider Range Input */}
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={compareSplit}
                        onChange={(e) => setCompareSplit(Number(e.target.value))}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-30"
                      />
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 h-[380px] lg:h-[420px]">
                      <div className="relative rounded-xl overflow-hidden border border-slate-200">
                        <img src={comparePreviewA} alt="Pass A" className="w-full h-full object-cover" />
                        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm border border-slate-200 rounded-lg px-2.5 py-1 text-[11px] font-semibold text-slate-800 shadow-xs">
                          Pass A (2024 Acquisition)
                        </div>
                      </div>
                      <div className="relative rounded-xl overflow-hidden border border-slate-200">
                        <img src={comparePreviewB} alt="Pass B" className="w-full h-full object-cover" />
                        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm border border-slate-200 rounded-lg px-2.5 py-1 text-[11px] font-semibold text-slate-800 shadow-xs">
                          Pass B (2026 Acquisition)
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Change Detection KPI Badges */}
                  <div className="grid grid-cols-3 gap-3 pt-2">
                    <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                        <Building2 size={16} />
                      </div>
                      <div>
                        <p className="font-display font-bold text-sm text-slate-900">+6 Structures</p>
                        <p className="text-[10.5px] text-slate-500">New Urban Buildings</p>
                      </div>
                    </div>

                    <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
                        <Trees size={16} />
                      </div>
                      <div>
                        <p className="font-display font-bold text-sm text-slate-900">-4.2% Canopy</p>
                        <p className="text-[10.5px] text-slate-500">Vegetation Reduction</p>
                      </div>
                    </div>

                    <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                        <Route size={16} />
                      </div>
                      <div>
                        <p className="font-display font-bold text-sm text-slate-900">+1.4 km</p>
                        <p className="text-[10.5px] text-slate-500">Road Extensions</p>
                      </div>
                    </div>
                  </div>
                </div>

                <AnalysisStats />
              </div>
            ) : (
              /* Single / Multi Scene Standard Analysis */
              <div className="space-y-4">
                <div className="h-[380px] lg:h-[420px] w-full">
                  <SatelliteViewer layers={layers} onToggleLayer={toggleLayer} />
                </div>
                <AnalysisStats />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right Desktop Chat Copilot */}
      <div className="hidden xl:block w-[380px] shrink-0 h-full">
        <ChatPanel onLayerSuggestion={activateFromChat} />
      </div>
    </div>
  )
}

function StepChip({ n, label, active }) {
  return (
    <div
      className={`rounded-2xl border px-3 py-3 shadow-xs transition-all ${
        active ? 'border-blue-500 bg-blue-50/50' : 'border-slate-200 bg-white'
      }`}
    >
      <p className={`font-display text-sm font-bold ${active ? 'text-blue-600' : 'text-slate-400'}`}>{n}</p>
      <p className={`text-xs mt-0.5 ${active ? 'text-slate-800 font-semibold' : 'text-slate-500'}`}>{label}</p>
    </div>
  )
}
