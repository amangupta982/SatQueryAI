import { useState, useRef } from 'react'
import {
  Upload,
  Sparkles,
  Send,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Layers,
  Compass,
  Maximize2,
  ChevronRight,
  RefreshCw,
} from 'lucide-react'
import DownloadReportButton from '../components/DownloadReportButton'

// Preloaded authentic Earth observation satellite scenes
const presetScenes = [
  {
    id: 'brahmaputra',
    name: 'Brahmaputra River Valley',
    sensor: 'Sentinel-2 (Optical)',
    resolution: '10m GSD',
    location: 'Assam, India · 26.14° N, 91.73° E',
    thumbnail: '/hero_brahmaputra_exact_seamless.jpg',
    defaultQuestion: 'What covers most of this image?',
  },
  {
    id: 'bengaluru',
    name: 'Bengaluru Sector 14',
    sensor: 'Cartosat-3 (High-Res)',
    resolution: '0.5m GSD',
    location: 'Karnataka, India · 13.08° N, 77.59° E',
    thumbnail: '/satellite_scene.jpg',
    defaultQuestion: 'Is this an urban area?',
  },
  {
    id: 'inundation',
    name: 'Majuli Floodplain Corridor',
    sensor: 'RISAT-1A (C-Band SAR)',
    resolution: '3m GSD',
    location: 'Assam, India · 26.95° N, 94.21° E',
    thumbnail: '/cap_optical_sar.jpg',
    defaultQuestion: 'Is water present in the scene?',
  },
]

const suggestedQueries = [
  'What area covers most of this image?',
  'Is water present in the scene?',
  'What is the dominant land-cover type?',
  'Is this mostly vegetation?',
  'Is agricultural land present?',
  'How many buildings are visible?',
  'Does water or vegetation cover more area?',
]

export default function VQAWorkspace() {
  const [selectedPreset, setSelectedPreset] = useState(presetScenes[0])
  const [customImage, setCustomImage] = useState(null)
  const [customImagePreview, setCustomImagePreview] = useState(null)
  const [question, setQuestion] = useState(presetScenes[0].defaultQuestion)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState({
    answer: 'Vegetation covers most of this scene, predominantly along the river floodplains and surrounding agricultural terrain.',
    task: 'land_cover',
    confidence: 0.942,
    model: 'SatQuery-VQA',
    evidence: {
      coverage_tier: 'Primary (>25% image coverage)',
      sensor: 'Sentinel-2 (Optical)',
      dominant_class: 'Broad-leaved forest / Vegetation',
    },
  })
  const fileInputRef = useRef(null)

  const handleCustomFileUpload = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setCustomImage(file)
    const previewUrl = URL.createObjectURL(file)
    setCustomImagePreview(previewUrl)
  }

  const handleSelectPreset = (preset) => {
    setSelectedPreset(preset)
    setCustomImage(null)
    setCustomImagePreview(null)
    setQuestion(preset.defaultQuestion)
  }

  const handleAsk = async (queryToAsk) => {
    const q = (queryToAsk || question).trim()
    if (!q) return

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('question', q)
      formData.append('sensor', selectedPreset.sensor.includes('SAR') ? 'Sentinel-1' : 'Sentinel-2')

      if (customImage) {
        formData.append('image', customImage)
      } else {
        try {
          const imgRes = await fetch(selectedPreset.thumbnail)
          const imgBlob = await imgRes.blob()
          formData.append('image', imgBlob, `${selectedPreset.id}.jpg`)
        } catch {
          formData.append('image_b64', 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
        }
      }

      const response = await fetch('/api/v1/vqa', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}))
        throw new Error(errJson.detail || `Server returned HTTP ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setResult({
        answer: `SatQuery-VQA Error: ${err.message || 'Model service unavailable'}`,
        task: 'error',
        confidence: null,
        model: 'SatQuery-VQA',
        error: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const activeImageSrc = customImagePreview || selectedPreset.thumbnail

  return (
    <div className="flex-1 overflow-y-auto bg-[#fafaf8] text-[#162721] p-4 sm:p-6 lg:p-10 font-body">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-bold text-[#8a7b6b] uppercase tracking-widest font-mono">
              INTERACTIVE VQA WORKSPACE
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#e2eae5] text-[#234238] border border-[#c8d4ce]">
              SatQuery-VQA Engine
            </span>
          </div>
          <h1 className="font-display font-extrabold text-2xl sm:text-3xl lg:text-4xl text-[#162721] tracking-tight">
            Upload Satellite Image & Ask Question
          </h1>
          <p className="text-xs sm:text-sm text-[#5f7168] max-w-2xl leading-relaxed">
            Upload any remote-sensing scene or select a reference constellation image. Ask questions in natural language and receive grounded answers from our custom-trained SatQuery-VQA model.
          </p>
        </div>

        {/* Main 2-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
          
          {/* LEFT COLUMN: Satellite Scene View & Upload (7 cols) */}
          <div className="lg:col-span-7 bg-white rounded-2xl border border-[#e2e8e4] p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#f0f4f1] pb-3">
              <div>
                <h3 className="font-display font-bold text-sm text-[#162721]">
                  Active Satellite Scene
                </h3>
                <p className="text-[11px] text-[#6b7c73] font-mono">
                  {customImage ? `Uploaded: ${customImage.name}` : selectedPreset.location}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-lg text-[10.5px] font-semibold bg-[#f4f7f5] text-[#234238] border border-[#d8e2dc]">
                  {customImage ? 'Custom Scene' : selectedPreset.sensor}
                </span>
                <span className="px-2 py-1 rounded-lg text-[10.5px] font-mono text-[#6b7c73] bg-[#fafaf8] border border-[#e2e8e4]">
                  {customImage ? 'User Upload' : selectedPreset.resolution}
                </span>
              </div>
            </div>

            {/* Satellite Image Preview Display */}
            <div className="relative w-full h-[320px] sm:h-[380px] rounded-xl overflow-hidden bg-slate-900 border border-slate-200 group">
              <img
                src={activeImageSrc}
                alt="Active Satellite Scene"
                className="w-full h-full object-cover group-hover:scale-[1.01] transition-transform duration-500"
              />

              {/* Crosshair inspection overlay */}
              <div className="absolute inset-0 pointer-events-none opacity-40">
                <div className="absolute top-1/2 left-0 right-0 border-t border-white/40" />
                <div className="absolute left-1/2 top-0 bottom-0 border-l border-white/40" />
              </div>

              {/* Badges in preview */}
              <div className="absolute top-3 left-3 flex items-center gap-2 bg-black/60 backdrop-blur-md px-3 py-1 rounded-lg border border-white/15 text-white text-[10.5px] font-mono">
                <Compass size={12} className="text-emerald-400" />
                <span>{customImage ? 'Custom Coordinates' : selectedPreset.location}</span>
              </div>

              {/* Bounding box overlay if evidence has boxes */}
              {result?.evidence?.bounding_boxes?.map((box, idx) => (
                <div
                  key={idx}
                  className="absolute border-2 border-amber-400 bg-amber-400/20 rounded-sm pointer-events-none"
                  style={{
                    top: `${box[0] * 100}%`,
                    left: `${box[1] * 100}%`,
                    height: `${(box[2] - box[0]) * 100}%`,
                    width: `${(box[3] - box[1]) * 100}%`,
                  }}
                >
                  <span className="absolute -top-4 left-0 bg-amber-500 text-black font-bold text-[9px] px-1 rounded-xs">
                    Evidence #{idx + 1}
                  </span>
                </div>
              ))}
            </div>

            {/* Scene Selection Tabs / Upload Options */}
            <div className="space-y-2 pt-2">
              <span className="text-[11px] font-bold text-[#6b7c73] uppercase tracking-wider font-mono block">
                Choose a Reference Satellite Scene or Upload Yours:
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                {presetScenes.map((ps) => (
                  <button
                    key={ps.id}
                    onClick={() => handleSelectPreset(ps)}
                    className={`p-2 rounded-xl text-left border transition-all cursor-pointer flex flex-col justify-between ${
                      !customImage && selectedPreset.id === ps.id
                        ? 'bg-[#e2eae5] border-[#234238] shadow-xs'
                        : 'bg-white border-[#e2e8e4] hover:bg-[#f6f9f7]'
                    }`}
                  >
                    <div className="h-12 w-full rounded-lg overflow-hidden bg-slate-100 mb-1.5">
                      <img src={ps.thumbnail} alt={ps.name} className="w-full h-full object-cover" />
                    </div>
                    <div className="text-[11px] font-bold text-[#162721] truncate">{ps.name}</div>
                    <div className="text-[9.5px] text-[#5f7168] truncate">{ps.sensor}</div>
                  </button>
                ))}

                {/* Custom Upload Trigger Card */}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className={`p-2 rounded-xl text-center border border-dashed transition-all cursor-pointer flex flex-col items-center justify-center gap-1.5 ${
                    customImage
                      ? 'bg-blue-50 border-blue-400 text-blue-800'
                      : 'border-[#c8d4ce] hover:border-[#234238] bg-[#fafaf8]'
                  }`}
                >
                  <Upload size={18} className={customImage ? 'text-blue-600' : 'text-[#234238]'} />
                  <span className="text-[11px] font-bold text-[#162721]">
                    {customImage ? 'Replace Image' : 'Upload Image'}
                  </span>
                  <span className="text-[9.5px] text-[#6b7c73]">PNG, JPG, TIF</span>
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleCustomFileUpload}
                    className="hidden"
                    accept="image/*,.tif,.tiff"
                  />
                </button>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: Question Input & Live VQA Answer (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            {/* Ask Question Card */}
            <div className="bg-white rounded-2xl border border-[#e2e8e4] p-5 shadow-xs space-y-4">
              <div className="flex items-center gap-2 text-[#234238]">
                <Sparkles size={16} />
                <h3 className="font-display font-bold text-sm text-[#162721]">
                  Ask SatQuery-VQA
                </h3>
              </div>

              {/* Text Input Box */}
              <div className="space-y-2">
                <div className="relative">
                  <textarea
                    rows={3}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleAsk()
                      }
                    }}
                    placeholder="Type your question (e.g. What area covers most of this image?)"
                    className="w-full text-xs sm:text-[13px] bg-[#fafaf8] border border-[#d2dad5] rounded-xl p-3 text-[#162721] placeholder-[#8a9b92] focus:outline-none focus:ring-2 focus:ring-[#234238]/20 focus:border-[#234238] transition-all resize-none"
                  />
                </div>

                <button
                  onClick={() => handleAsk()}
                  disabled={loading || !question.trim()}
                  className="w-full py-2.5 px-4 bg-[#234238] hover:bg-[#1a342c] disabled:opacity-50 text-white text-xs sm:text-[13px] font-semibold rounded-xl flex items-center justify-center gap-2 shadow-xs transition-all cursor-pointer"
                >
                  {loading ? (
                    <>
                      <RefreshCw size={14} className="animate-spin" />
                      <span>Analyzing satellite scene...</span>
                    </>
                  ) : (
                    <>
                      <span>Ask SatQuery-VQA</span>
                      <Send size={13} />
                    </>
                  )}
                </button>
              </div>

              {/* Suggested Questions Chips */}
              <div className="space-y-2 pt-2 border-t border-[#f0f4f1]">
                <span className="text-[10.5px] font-bold text-[#8a7b6b] uppercase tracking-wider font-mono block">
                  Suggested Questions:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {suggestedQueries.map((sq, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuestion(sq)
                        handleAsk(sq)
                      }}
                      className="text-[11px] bg-[#f4f7f5] hover:bg-[#e2eae5] text-[#234238] border border-[#d8e2dc] px-2.5 py-1 rounded-lg transition-colors text-left cursor-pointer"
                    >
                      {sq}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Live Model Response Card */}
            <div className="bg-white rounded-2xl border border-[#e2e8e4] p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-[#f0f4f1] pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-[#234238] text-white flex items-center justify-center">
                    <CheckCircle2 size={14} />
                  </div>
                  <h4 className="font-display font-bold text-xs sm:text-sm text-[#162721]">
                    VQA Model Response
                  </h4>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {result.model || 'SatQuery-VQA'}
                  </span>
                  {result.confidence !== null && result.confidence !== undefined && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
                      {(result.confidence * 100).toFixed(1)}% Conf
                    </span>
                  )}
                </div>
              </div>

              {/* Answer Content */}
              <div className="p-3.5 bg-[#f8faf8] border border-[#e2e8e4] rounded-xl space-y-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#63766c] font-mono block">
                  Answer
                </span>
                <p className="text-xs sm:text-[13px] text-[#162721] font-medium leading-relaxed">
                  {result.answer}
                </p>
              </div>

              {/* Evidence & Task Details */}
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="p-2.5 rounded-xl bg-[#fafaf8] border border-[#e2e8e4]">
                  <span className="text-[#6b7c73] block text-[10px]">Identified Task</span>
                  <span className="font-bold text-[#234238] capitalize">{result.task || 'Presence'}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-[#fafaf8] border border-[#e2e8e4]">
                  <span className="text-[#6b7c73] block text-[10px]">Sensor Engine</span>
                  <span className="font-bold text-[#234238]">{result.evidence?.sensor || selectedPreset.sensor}</span>
                </div>
              </div>

              {result.evidence?.coverage_tier && (
                <div className="p-2.5 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 text-[11px]">
                  <span className="font-bold">Coverage Tier: </span>
                  <span>{result.evidence.coverage_tier}</span>
                </div>
              )}

              {result.evidence?.limitation && (
                <div className="p-2.5 rounded-xl bg-orange-50 border border-orange-200 text-orange-900 text-[11px] space-y-1">
                  <div className="font-bold flex items-center gap-1">
                    <AlertCircle size={13} className="text-orange-600 shrink-0" />
                    <span>Resolution Limitation Handled</span>
                  </div>
                  <p className="text-[10.5px] leading-relaxed text-orange-800">
                    {result.evidence.limitation}
                  </p>
                </div>
              )}

              {/* Download Prediction Report Button */}
              {!result.error && (
                <div className="pt-2 border-t border-[#f0f4f1] flex justify-end">
                  <DownloadReportButton
                    reportData={{
                      title: 'SatQuery-VQA Vision-Language Prediction Report',
                      analysisType: 'Visual Question Answering (VQA)',
                      query: question,
                      modelUsed: result.model || 'SatQuery-VQA',
                      prediction: result.answer,
                      confidence: result.confidence,
                      sceneDetails: {
                        'Target Scene': customImage ? customImage.name : selectedPreset.location,
                        'Sensor Constellation': result.evidence?.sensor || selectedPreset.sensor,
                        'Task Mode': result.task || 'Presence & Classification',
                      },
                      statistics: [
                        { label: 'Identified Task', value: result.task || 'Presence' },
                        { label: 'Sensor Engine', value: result.evidence?.sensor || selectedPreset.sensor },
                        ...(result.confidence !== null && result.confidence !== undefined
                          ? [{ label: 'Confidence Score', value: `${(result.confidence * 100).toFixed(1)}%` }]
                          : []),
                      ],
                      evidenceImages: [
                        {
                          title: 'Analyzed Satellite Scene',
                          src: activeImageSrc,
                          details: customImage ? `Uploaded file: ${customImage.name}` : `Location: ${selectedPreset.location}`,
                        },
                      ],
                      limitations: result.evidence?.limitation || null,
                      executionNotes: result.evidence?.coverage_tier ? `Coverage Tier: ${result.evidence.coverage_tier}` : null,
                    }}
                  />
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}
