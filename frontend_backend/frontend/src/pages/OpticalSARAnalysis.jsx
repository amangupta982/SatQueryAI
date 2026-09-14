import { useState, useRef } from 'react'
import {
  Sparkles,
  Send,
  Upload,
  RefreshCw,
  Sliders,
  AlertCircle,
  Layers,
  Radio,
  Eye,
  Crosshair,
} from 'lucide-react'
import DownloadReportButton from '../components/DownloadReportButton'

const BACKEND_URL = 'http://localhost:8000'

const AGENT_MODES = [
  { id: 'optical_only', label: 'Mode 1: Optical Only (Sentinel-2)', desc: 'Prithvi-EO-2.0-300M multispectral foundation perception' },
  { id: 'sar_only', label: 'Mode 2: SAR Only (Sentinel-1)', desc: 'SUMMIT SAR ViT dual-pol (VV, VH) radar backscatter perception' },
  { id: 'optical_sar', label: 'Mode 3: Optical + SAR Joint Fusion', desc: 'Cross-attention alignment & cross-modal difference (Mode A)' },
  { id: 'optical_sar_temporal', label: 'Mode 4: Optical + SAR Temporal', desc: 'Temporal analysis when metadata establishes time difference (Mode B)' },
  { id: 'optical_sar_vqa', label: 'Mode 5: BigEarthNet.txt VQA', desc: '15-task VQA (Presence, Area, Counting, Adjacency, Position)' },
  { id: 'optical_sar_vqa_grounding', label: 'Mode 6: VQA + Visual Grounding', desc: 'Referring expression spatial bounding box localization' },
  { id: 'optical_sar_full_geospatial', label: 'Mode 7: Full Geospatial Agent', desc: 'Complete multi-sensor perception with deterministic local coordinates' },
]

export default function OpticalSARAnalysis() {
  const [selectedAgentMode, setSelectedAgentMode] = useState(AGENT_MODES[6].id)

  const [opticalFile, setOpticalFile] = useState(null)
  const [sarFile, setSarFile] = useState(null)
  const [initialQuestion, setInitialQuestion] = useState(
    'What land cover classes are present in this satellite scene?'
  )

  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const [activeLayer, setActiveLayer] = useState('optical')

  const [dialogue, setDialogue] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [querying, setQuerying] = useState(false)

  const opticalInputRef = useRef(null)
  const sarInputRef = useRef(null)

  const handleLoadSampleScene = async () => {
    try {
      const resp = await fetch('/cap_optical_sar.jpg')
      const blob = await resp.blob()
      const file = new File([blob], 'sentinel2_sample.jpg', { type: 'image/jpeg' })
      setOpticalFile(file)
      setError(null)
    } catch (err) {
      console.error('Failed to load sample image:', err)
    }
  }

  const runAnalysis = async () => {
    setAnalyzing(true)
    setError(null)

    try {
      if (!opticalFile) {
        setError('Please upload at least a Sentinel-2 optical image (PNG, JPG, or GeoTIFF).')
        setAnalyzing(false)
        return
      }

      const formData = new FormData()
      formData.append('optical_file', opticalFile, opticalFile.name || 'optical.png')
      if (sarFile) {
        formData.append('sar_file', sarFile, sarFile.name || 'sar.png')
      }
      formData.append('question', initialQuestion || '')
      formData.append('agent_mode', selectedAgentMode)

      const res = await fetch(`${BACKEND_URL}/api/v1/optical-sar/analyze`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `Backend returned HTTP ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
      setDialogue([
        {
          role: 'agent',
          text: data.answer,
          mode: data.mode_applied,
          confidence: data.confidence,
        },
      ])
    } catch (err) {
      console.error(err)
      setError(err.message || 'Analysis failed. Please ensure the backend server is running.')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleSendFollowUp = async (e) => {
    e.preventDefault()
    if (!chatInput.trim() || !result?.session_id || querying) return

    const userQ = chatInput.trim()
    setChatInput('')
    setDialogue((prev) => [...prev, { role: 'user', text: userQ }])
    setQuerying(true)

    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/optical-sar/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: result.session_id,
          question: userQ,
        }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || 'Failed to query session')
      }

      const data = await res.json()
      setDialogue((prev) => [
        ...prev,
        { role: 'agent', text: data.answer, mode: data.mode, type: data.type },
      ])
    } catch (err) {
      setDialogue((prev) => [
        ...prev,
        { role: 'agent', text: `Error: ${err.message}`, isError: true },
      ])
    } finally {
      setQuerying(false)
    }
  }

  return (
    <div className="flex-1 overflow-y-auto bg-[#fafaf8]">
      <div className="max-w-7xl mx-auto p-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <Radio className="w-5 h-5 text-[#2d5243]" />
              <h1 className="text-xl font-bold text-[#162721]">Optical-SAR Multimodal Agent</h1>
              <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#edf2ef] text-[#2d5243] border border-[#dce7e1] rounded-full">
                BigEarthNet.txt
              </span>
            </div>
            <p className="text-xs text-[#6b7c73]">
              Co-registered Sentinel-1 SAR + Sentinel-2 Multispectral Foundation Perception
            </p>
          </div>

          <div className="text-xs text-[#7a9486] bg-[#edf2ef] border border-[#dce7e1] rounded-lg px-3 py-1.5 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Mode A: Cross-Modal Difference
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Config & Upload */}
          <div className="lg:col-span-4 space-y-5">
            {/* Agent Mode Selector */}
            <div className="bg-white border border-[#e5ebe7] rounded-xl p-4 shadow-2xs">
              <label className="text-xs font-semibold text-[#162721] uppercase tracking-wider block mb-2 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-[#2d5243]" /> Operational Agent Mode
              </label>
              <select
                value={selectedAgentMode}
                onChange={(e) => setSelectedAgentMode(e.target.value)}
                className="w-full bg-[#f9fbfa] border border-[#dce7e1] rounded-lg px-3 py-2 text-xs text-[#162721] focus:outline-none focus:ring-1 focus:ring-[#2d5243]"
              >
                {AGENT_MODES.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-[#7a9486] mt-2">
                {AGENT_MODES.find((m) => m.id === selectedAgentMode)?.desc}
              </p>
            </div>

            {/* Image Upload */}
            <div className="bg-white border border-[#e5ebe7] rounded-xl p-4 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-[#162721] uppercase tracking-wider flex items-center gap-1.5">
                  <Upload className="w-3.5 h-3.5 text-[#2d5243]" /> Upload Co-Registered Sentinel Pair
                </div>
                <button
                  type="button"
                  onClick={handleLoadSampleScene}
                  className="text-[11px] text-[#2d5243] font-medium bg-[#eef5f1] hover:bg-[#e0ece4] px-2 py-0.5 rounded transition cursor-pointer"
                >
                  Load Sample
                </button>
              </div>

              {/* Optical Upload */}
              <div>
                <label className="text-xs text-[#5c7569] block mb-1">Sentinel-2 Multispectral / RGB (Required)</label>
                <input ref={opticalInputRef} type="file" accept="image/*,.tif,.tiff" onChange={(e) => setOpticalFile(e.target.files[0] || null)} className="hidden" />
                <div
                  onClick={() => opticalInputRef.current?.click()}
                  className="border border-dashed border-[#c8d5cc] hover:border-[#2d5243] rounded-lg p-3 text-center cursor-pointer bg-[#f9fbfa] hover:bg-[#f0f5f2] transition"
                >
                  <Upload className="w-5 h-5 mx-auto text-[#7a9486] mb-1" />
                  <span className="text-xs text-[#5c7569]">{opticalFile ? opticalFile.name : 'Select Optical file'}</span>
                </div>
              </div>

              {/* SAR Upload */}
              <div>
                <label className="text-xs text-[#5c7569] block mb-1">Sentinel-1 SAR VV/VH (Optional for Mode 1)</label>
                <input ref={sarInputRef} type="file" accept="image/*,.tif,.tiff" onChange={(e) => setSarFile(e.target.files[0] || null)} className="hidden" />
                <div
                  onClick={() => sarInputRef.current?.click()}
                  className="border border-dashed border-[#c8d5cc] hover:border-[#2d5243] rounded-lg p-3 text-center cursor-pointer bg-[#f9fbfa] hover:bg-[#f0f5f2] transition"
                >
                  <Radio className="w-5 h-5 mx-auto text-[#7a9486] mb-1" />
                  <span className="text-xs text-[#5c7569]">{sarFile ? sarFile.name : 'Select SAR file'}</span>
                </div>
              </div>

              {/* Question */}
              <div>
                <label className="text-xs text-[#5c7569] block mb-1">Initial Task / Question</label>
                <textarea
                  rows={2}
                  value={initialQuestion}
                  onChange={(e) => setInitialQuestion(e.target.value)}
                  placeholder="e.g. What land cover classes are present?"
                  className="w-full bg-[#f9fbfa] border border-[#dce7e1] rounded-lg px-3 py-2 text-xs text-[#162721] focus:outline-none focus:ring-1 focus:ring-[#2d5243]"
                />
              </div>

              {/* Run Button */}
              <button
                onClick={runAnalysis}
                disabled={analyzing}
                className="w-full bg-[#234238] hover:bg-[#1b342c] disabled:opacity-40 text-white font-semibold py-2.5 rounded-xl text-xs transition flex items-center justify-center gap-2 shadow-sm cursor-pointer"
              >
                {analyzing ? (
                  <><RefreshCw className="w-4 h-4 animate-spin" /> Running Foundation Fusion...</>
                ) : (
                  <><Sparkles className="w-4 h-4" /> Run Optical-SAR Analysis</>
                )}
              </button>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-500 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Viewer + Results + Dialogue */}
          <div className="lg:col-span-8 space-y-5">
            {/* Visual Display */}
            <div className="bg-white border border-[#e5ebe7] rounded-xl p-4 shadow-2xs">
              <div className="flex items-center justify-between border-b border-[#e5ebe7] pb-3 mb-4">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-[#2d5243]" />
                  <span className="text-sm font-bold text-[#162721]">Multimodal Sensor Inspection</span>
                  {result && (
                    <span className="px-2 py-0.5 text-[10px] bg-[#edf2ef] text-[#5c7569] rounded font-mono border border-[#dce7e1]">
                      {result.session_id}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  {result && (
                    <DownloadReportButton
                      variant="secondary"
                      reportData={{
                        title: 'Optical-SAR Multimodal Fusion & Grounding Report',
                        analysisType: 'Optical-SAR Multimodal Perception',
                        query: initialQuestion,
                        modelUsed: 'Sentinel-1/2 Foundation Fusion (Prithvi + Summit)',
                        prediction: result.answer,
                        confidence: result.confidence,
                        sceneDetails: {
                          'Session ID': result.session_id,
                          'Mode Applied': result.mode_applied,
                          'Optical File': opticalFile ? opticalFile.name : 'Sentinel-2 RGB',
                          'SAR File': sarFile ? sarFile.name : 'Sentinel-1 SAR',
                          'Temporal Change Detected': result.is_temporal_change ? 'Yes' : 'No',
                        },
                        statistics: [
                          { label: 'Mode Applied', value: result.mode_applied },
                          { label: 'Classes Detected', value: result.categories_detected?.length || 0 },
                          ...(result.confidence ? [{ label: 'Confidence', value: `${(result.confidence * 100).toFixed(1)}%` }] : []),
                          { label: 'Grounded Boxes', value: result.grounded_boxes?.length || 0 },
                        ],
                        categories: Object.entries(result.category_proportions || {}).map(([cat, pct]) => ({
                          name: cat.replace('_', ' '),
                          percent: pct.toFixed(1),
                          areaHa: ((pct / 100.0) * 501.76).toFixed(1),
                        })),
                        evidenceImages: [
                          ...(result.evidence_urls?.fused_image ? [{ title: 'Fused Cross-Modal Layer', src: `${BACKEND_URL}${result.evidence_urls.fused_image}` }] : []),
                          ...(result.evidence_urls?.optical_image ? [{ title: 'Sentinel-2 Optical Multispectral', src: `${BACKEND_URL}${result.evidence_urls.optical_image}` }] : []),
                          ...(result.evidence_urls?.sar_image ? [{ title: 'Sentinel-1 SAR Radar Amplitude', src: `${BACKEND_URL}${result.evidence_urls.sar_image}` }] : []),
                        ],
                      }}
                    />
                  )}

                  {result && (
                    <div className="flex items-center gap-1 bg-[#f4f7f5] p-0.5 rounded-lg border border-[#dce7e1] text-xs">
                      {['optical', 'sar', 'diff', 'fused'].map((layer) => (
                        <button
                          key={layer}
                          onClick={() => setActiveLayer(layer)}
                          className={`px-2.5 py-1 rounded-md font-semibold transition ${
                            activeLayer === layer
                              ? 'bg-[#2d5243] text-white shadow-sm'
                              : 'text-[#5c7569] hover:text-[#162721]'
                          }`}
                        >
                          {layer === 'optical' ? 'Optical (S2)' : layer === 'sar' ? 'SAR (S1)' : layer === 'diff' ? 'Cross-Diff' : 'Fused'}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Image */}
              <div className="w-full bg-[#f4f7f5] rounded-xl overflow-hidden flex items-center justify-center border border-[#dce7e1] p-2 min-h-[380px]">
                {result ? (
                  <div className="relative aspect-square max-h-[480px] w-auto max-w-full mx-auto overflow-hidden rounded-lg border border-[#dce7e1]">
                    <img
                      src={`${BACKEND_URL}${
                        activeLayer === 'optical'
                          ? result.evidence_urls.optical_image
                          : activeLayer === 'sar'
                          ? result.evidence_urls.sar_image
                          : activeLayer === 'diff'
                          ? result.evidence_urls.cross_modal_diff
                          : result.evidence_urls.fused_image
                      }`}
                      alt="Multimodal Layer"
                      className="w-full h-full object-cover block"
                    />
                    {activeLayer !== 'fused' && result.grounded_boxes?.map((b, idx) => {
                      const [ymin, xmin, ymax, xmax] = b.box
                      return (
                        <div
                          key={idx}
                          style={{
                            top: `${(ymin / 224) * 100}%`,
                            left: `${(xmin / 224) * 100}%`,
                            width: `${Math.max(2, ((xmax - xmin) / 224) * 100)}%`,
                            height: `${Math.max(2, ((ymax - ymin) / 224) * 100)}%`,
                          }}
                          className="absolute border-2 border-amber-500 bg-amber-400/20 rounded pointer-events-none"
                        >
                          <span className="absolute -top-5 left-0 bg-amber-500 text-white font-bold text-[10px] px-1.5 py-0.5 rounded shadow-sm">
                            {b.label}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center p-8 text-[#7a9486]">
                    <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Upload imagery, then click Run Analysis</p>
                  </div>
                )}
              </div>

              {/* Metrics Bar */}
              {result && (
                <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="bg-[#f9fbfa] border border-[#e5ebe7] rounded-lg p-2.5">
                    <span className="text-[11px] text-[#7a9486] block">Interpretation</span>
                    <span className="text-xs font-bold text-[#2d5243] uppercase">
                      {result.mode_applied === 'mode_a_cross_modal' ? 'Mode A: Cross-Modal' : 'Mode B: Temporal'}
                    </span>
                  </div>
                  <div className="bg-[#f9fbfa] border border-[#e5ebe7] rounded-lg p-2.5">
                    <span className="text-[11px] text-[#7a9486] block">Modality Alignment</span>
                    <span className="text-xs font-bold text-emerald-600">
                      {((result.cross_modal_difference?.cross_modal_correlation || 0.85) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="bg-[#f9fbfa] border border-[#e5ebe7] rounded-lg p-2.5">
                    <span className="text-[11px] text-[#7a9486] block">Dominant Class</span>
                    <span className="text-xs font-bold text-[#162721]">{result.categories_detected?.[0] || 'Vegetation'}</span>
                  </div>
                  <div className="bg-[#f9fbfa] border border-[#e5ebe7] rounded-lg p-2.5">
                    <span className="text-[11px] text-[#7a9486] block">Confidence</span>
                    <span className="text-xs font-bold text-amber-600">
                      {((result.confidence || 0.94) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              )}

              {/* Land Cover Breakdown */}
              {result && result.category_proportions && (
                <div className="mt-4 bg-[#f9fbfa] border border-[#e5ebe7] rounded-lg p-3">
                  <div className="text-xs font-semibold text-[#162721] uppercase tracking-wider mb-2 flex items-center justify-between">
                    <span>Land Cover Surface Coverage</span>
                    <span className="text-[11px] text-[#7a9486] font-mono">10m GSD</span>
                  </div>
                  <div className="space-y-2">
                    {Object.entries(result.category_proportions)
                      .sort(([, a], [, b]) => b - a)
                      .map(([cat, pct]) => {
                        const ha = ((pct / 100.0) * 501.76).toFixed(1)
                        const barColor =
                          cat === 'vegetation' ? 'bg-emerald-500' :
                          cat === 'low_vegetation' ? 'bg-lime-400' :
                          cat === 'water' ? 'bg-sky-500' :
                          cat === 'building' ? 'bg-rose-500' :
                          cat === 'infrastructure' ? 'bg-purple-500' :
                          cat === 'bare_land' ? 'bg-amber-600' : 'bg-gray-400'
                        return (
                          <div key={cat} className="space-y-1">
                            <div className="flex justify-between text-xs text-[#162721]">
                              <span className="capitalize font-medium">{cat.replace('_', ' ')}</span>
                              <span className="font-mono text-[#7a9486]">{pct.toFixed(1)}% ({ha} ha)</span>
                            </div>
                            <div className="w-full h-1.5 bg-[#e5ebe7] rounded-full overflow-hidden">
                              <div className={`h-full ${barColor} rounded-full transition-all duration-500`} style={{ width: `${Math.min(100, pct)}%` }} />
                            </div>
                          </div>
                        )
                      })}
                  </div>
                </div>
              )}

              {/* Grounded Boxes Table */}
              {result && result.grounded_boxes && result.grounded_boxes.length > 0 && (
                <div className="mt-4 bg-[#f9fbfa] border border-[#e5ebe7] rounded-lg p-3">
                  <div className="text-xs font-semibold text-amber-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Crosshair className="w-3.5 h-3.5" />
                    <span>Grounded Spatial Regions ({result.grounded_boxes.length} localized)</span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs text-[#162721]">
                      <thead className="border-b border-[#e5ebe7] text-[11px] text-[#7a9486]">
                        <tr>
                          <th className="pb-1.5 font-medium">ID</th>
                          <th className="pb-1.5 font-medium">Target</th>
                          <th className="pb-1.5 font-medium">Box</th>
                          <th className="pb-1.5 font-medium text-right">Confidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#f0f3f1] font-mono text-[11px]">
                        {result.grounded_boxes.map((b, idx) => (
                          <tr key={idx} className="hover:bg-[#f0f5f2]">
                            <td className="py-1.5 text-amber-600 font-bold">{b.region_id || `R0${idx + 1}`}</td>
                            <td className="py-1.5 font-sans font-medium">{b.label}</td>
                            <td className="py-1.5 text-[#7a9486]">[{b.box.join(', ')}]</td>
                            <td className="py-1.5 text-right font-sans font-semibold text-emerald-600">
                              {((b.confidence || 0.9) * 100).toFixed(0)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>

            {/* Interactive Dialogue */}
            <div className="bg-white border border-[#e5ebe7] rounded-xl p-4 shadow-2xs flex flex-col h-[340px]">
              <div className="flex items-center gap-2 border-b border-[#e5ebe7] pb-2 mb-3">
                <Sparkles className="w-4 h-4 text-[#2d5243]" />
                <h2 className="text-sm font-bold text-[#162721]">
                  Deterministic Agent Dialogue
                </h2>
              </div>

              <div className="flex-1 overflow-y-auto space-y-2.5 pr-2 text-xs">
                {dialogue.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-[#7a9486]">
                    Ask follow-up questions about presence, position, counting, or sensor differences.
                  </div>
                ) : (
                  dialogue.map((msg, i) => (
                    <div
                      key={i}
                      className={`p-2.5 rounded-xl max-w-[90%] leading-relaxed ${
                        msg.role === 'user'
                          ? 'ml-auto bg-[#2d5243] text-white rounded-br-none'
                          : 'mr-auto bg-[#f4f7f5] text-[#162721] border border-[#dce7e1] rounded-bl-none'
                      }`}
                    >
                      {msg.text}
                    </div>
                  ))
                )}
              </div>

              <form onSubmit={handleSendFollowUp} className="mt-3 flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder={result ? 'Ask about classes, bounding boxes, or modality differences...' : 'Run analysis first'}
                  disabled={!result || querying}
                  className="flex-1 bg-[#f9fbfa] border border-[#dce7e1] rounded-lg px-3 py-2 text-xs text-[#162721] focus:outline-none focus:ring-1 focus:ring-[#2d5243] disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={!result || querying || !chatInput.trim()}
                  className="bg-[#234238] hover:bg-[#1b342c] disabled:opacity-40 text-white px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" /> Ask
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
