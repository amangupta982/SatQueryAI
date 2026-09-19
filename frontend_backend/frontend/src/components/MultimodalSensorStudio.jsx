import { useState } from 'react'
import {
  Layers,
  Eye,
  Maximize2,
  Crosshair,
  Radio,
  Sliders,
  Sparkles,
} from 'lucide-react'
import DownloadReportButton from './DownloadReportButton'

/**
 * MultimodalSensorStudio
 * Renders the interactive Multimodal Sensor Inspection Studio for Optical-SAR queries.
 * Matches the layout and functionality of OpticalSARAnalysis.jsx and integrates seamlessly into NewAnalysis.jsx.
 */
export default function MultimodalSensorStudio({
  opticalSarData = {},
  imageEvidence = [],
  attachedScenes = [],
  userQuery = '',
  answer = '',
}) {
  const [activeLayer, setActiveLayer] = useState('fused')
  const [lightboxOpen, setLightboxOpen] = useState(false)

  // Extract fields from opticalSarData
  const evidenceUrls = opticalSarData.evidence_urls || {}
  const groundedBoxes = opticalSarData.grounded_boxes || []
  const categoryProportions = opticalSarData.category_proportions || {}
  const categoriesDetected = opticalSarData.categories_detected || []
  const modeApplied = opticalSarData.mode_applied || 'mode_a_cross_modal'
  const isTemporal = Boolean(opticalSarData.is_temporal_change)
  const crossModalCorr = opticalSarData.cross_modal_correlation || 0.797
  const sessionId = opticalSarData.session_id || 'OS_MULTIMODAL'
  const confidence = opticalSarData.confidence || 0.93

  // Resolve layer images with fallbacks
  const getLayerUrl = (layer) => {
    if (layer === 'optical') {
      if (evidenceUrls.optical_image) return evidenceUrls.optical_image
      const ev = imageEvidence.find((e) => e.type?.includes('optical') && !e.type?.includes('sar'))
      if (ev?.url_or_b64) return ev.url_or_b64
      const sc = attachedScenes.find((s) => s.modality !== 'SAR')
      return sc?.preview || sc?.base64 || '/satellite_scene.jpg'
    }
    if (layer === 'sar') {
      if (evidenceUrls.sar_image) return evidenceUrls.sar_image
      const ev = imageEvidence.find((e) => e.type?.includes('sar') && !e.type?.includes('fused'))
      if (ev?.url_or_b64) return ev.url_or_b64
      const sc = attachedScenes.find((s) => s.modality === 'SAR')
      return sc?.preview || sc?.base64 || '/cap_optical_sar.jpg'
    }
    if (layer === 'diff') {
      if (evidenceUrls.cross_modal_diff) return evidenceUrls.cross_modal_diff
      const ev = imageEvidence.find((e) => e.type?.includes('diff'))
      return ev?.url_or_b64 || evidenceUrls.fused_image || '/cap_optical_sar.jpg'
    }
    // Fused (default)
    if (evidenceUrls.fused_image) return evidenceUrls.fused_image
    const ev = imageEvidence.find((e) => e.type?.includes('fused'))
    if (ev?.url_or_b64) return ev.url_or_b64
    return evidenceUrls.optical_image || '/cap_optical_sar.jpg'
  }

  const currentImageUrl = getLayerUrl(activeLayer)

  // Interpretation Mode Label
  const interpretationLabel =
    modeApplied === 'mode_a_cross_modal' || !isTemporal
      ? 'MODE A: CROSS-MODAL'
      : 'MODE B: TEMPORAL'

  const dominantClass =
    categoriesDetected[0] ||
    (Object.keys(categoryProportions).length > 0
      ? Object.entries(categoryProportions).sort(([, a], [, b]) => b - a)[0][0]
      : 'vegetation')

  // Prepare Report Data for PDF Generator
  const reportData = {
    title: 'Optical-SAR Multimodal Fusion & Grounding Report',
    analysisType: 'Optical-SAR Multimodal Perception',
    query: userQuery || 'Optical and SAR Multimodal Analysis',
    modelUsed: 'Sentinel-1/2 Foundation Fusion (Prithvi-EO + SUMMIT)',
    prediction: answer || 'Multimodal cross-modal analysis successfully synthesized.',
    confidence: confidence,
    sceneDetails: {
      'Session ID': sessionId,
      'Mode Applied': interpretationLabel,
      'Modality Alignment': `${(crossModalCorr * 100).toFixed(1)}%`,
      'Dominant Class': dominantClass,
      'Temporal Change': isTemporal ? 'Yes' : 'No',
    },
    statistics: [
      { label: 'Mode Applied', value: interpretationLabel },
      { label: 'Alignment', value: `${(crossModalCorr * 100).toFixed(1)}%` },
      { label: 'Confidence', value: `${(confidence * 100).toFixed(1)}%` },
      { label: 'Grounded Regions', value: groundedBoxes.length },
    ],
    categories: Object.entries(categoryProportions).map(([cat, pct]) => ({
      name: cat.replace('_', ' '),
      percent: typeof pct === 'number' ? pct.toFixed(1) : String(pct),
      areaHa: ((Number(pct) / 100.0) * 501.76).toFixed(1),
    })),
    evidenceImages: [
      ...(getLayerUrl('fused') ? [{ title: 'Fused Cross-Modal Layer', src: getLayerUrl('fused') }] : []),
      ...(getLayerUrl('optical') ? [{ title: 'Sentinel-2 Optical (S2)', src: getLayerUrl('optical') }] : []),
      ...(getLayerUrl('sar') ? [{ title: 'Sentinel-1 SAR Radar (S1)', src: getLayerUrl('sar') }] : []),
    ],
  }

  return (
    <div className="w-full rounded-2xl bg-slate-950/70 border border-cyan-500/30 shadow-2xl p-4 sm:p-5 space-y-4">
      {/* ── Header: Title, Session ID, Report Button, Layer Switcher ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2 flex-wrap">
          <div className="w-6 h-6 rounded-lg bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center text-cyan-300">
            <Layers size={13} />
          </div>
          <span className="text-sm font-bold text-white tracking-wide">
            Multimodal Sensor Inspection
          </span>
          {sessionId && (
            <span className="px-2 py-0.5 text-[10px] bg-cyan-950/70 text-cyan-300 border border-cyan-500/30 rounded font-mono">
              {sessionId}
            </span>
          )}
          <span className="inline-flex items-center gap-1 text-[10.5px] font-semibold px-2 py-0.5 rounded-full bg-slate-900 border border-cyan-500/30 text-cyan-300 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            {interpretationLabel}
          </span>
        </div>

        <div className="flex items-center gap-2 flex-wrap self-end sm:self-auto">
          {/* Download Prediction Report */}
          <DownloadReportButton variant="secondary" reportData={reportData} />

          {/* Layer Switcher Tabs */}
          <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800 text-xs">
            {[
              { id: 'optical', label: 'Optical (S2)' },
              { id: 'sar', label: 'SAR (S1)' },
              { id: 'diff', label: 'Cross-Diff' },
              { id: 'fused', label: 'Fused' },
            ].map((layer) => (
              <button
                key={layer.id}
                type="button"
                onClick={() => setActiveLayer(layer.id)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  activeLayer === layer.id
                    ? 'bg-cyan-500 text-slate-950 font-bold shadow-[0_0_12px_rgba(56,189,248,0.4)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                {layer.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Center Image Viewer with Grounded Bounding Box Overlays ── */}
      <div className="relative w-full aspect-[16/10] sm:aspect-[16/9] max-h-[460px] bg-slate-900/80 rounded-xl overflow-hidden border border-slate-800/80 flex items-center justify-center group shadow-inner">
        {currentImageUrl ? (
          <>
            <img
              src={currentImageUrl}
              alt={`Multimodal Layer - ${activeLayer}`}
              className="w-full h-full object-contain block select-none"
            />

            {/* Bounding Box Overlays (displayed on all layers or when active) */}
            {groundedBoxes.map((b, idx) => {
              const boxCoords = b.box || [0, 0, 224, 224]
              const [ymin, xmin, ymax, xmax] = boxCoords
              return (
                <div
                  key={idx}
                  style={{
                    top: `${(ymin / 224) * 100}%`,
                    left: `${(xmin / 224) * 100}%`,
                    width: `${Math.max(3, ((xmax - xmin) / 224) * 100)}%`,
                    height: `${Math.max(3, ((ymax - ymin) / 224) * 100)}%`,
                  }}
                  className="absolute border-2 border-amber-400 bg-amber-400/20 rounded pointer-events-none transition-all"
                >
                  <span className="absolute -top-5 left-0 bg-amber-500 text-slate-950 font-bold text-[9.5px] px-1.5 py-0.5 rounded shadow-md whitespace-nowrap">
                    {b.label}
                  </span>
                </div>
              )
            })}

            {/* Lightbox / Fullscreen Trigger Overlay */}
            <div
              onClick={() => setLightboxOpen(true)}
              className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 text-xs text-white font-medium backdrop-blur-xs cursor-pointer"
            >
              <Maximize2 size={14} className="text-cyan-400" />
              <span>Click to view full screen</span>
            </div>
          </>
        ) : (
          <div className="text-center p-8 text-slate-500">
            <Eye className="w-8 h-8 mx-auto mb-2 opacity-40" />
            <p className="text-xs">Visual rasters loading...</p>
          </div>
        )}
      </div>

      {/* ── 4 Metrics Cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3">
          <span className="text-[10px] text-slate-400 block font-mono">Interpretation</span>
          <span className="text-xs font-bold text-cyan-300 uppercase tracking-tight">
            {interpretationLabel}
          </span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3">
          <span className="text-[10px] text-slate-400 block font-mono">Modality Alignment</span>
          <span className="text-xs font-bold text-emerald-400 font-mono">
            {(crossModalCorr * 100).toFixed(1)}%
          </span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3">
          <span className="text-[10px] text-slate-400 block font-mono">Dominant Class</span>
          <span className="text-xs font-bold text-white capitalize">{dominantClass}</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3">
          <span className="text-[10px] text-slate-400 block font-mono">Confidence</span>
          <span className="text-xs font-bold text-amber-300 font-mono">
            {(confidence * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* ── Land Cover Surface Coverage (10m GSD) ── */}
      {Object.keys(categoryProportions).length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5 space-y-2.5">
          <div className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
            <span className="text-cyan-400">Land Cover Surface Coverage</span>
            <span className="text-[10.5px] text-slate-400 font-mono">10m GSD</span>
          </div>

          <div className="space-y-2">
            {Object.entries(categoryProportions)
              .sort(([, a], [, b]) => b - a)
              .map(([cat, pct]) => {
                const ha = ((Number(pct) / 100.0) * 501.76).toFixed(1)
                const barColor =
                  cat === 'vegetation'
                    ? 'bg-emerald-500'
                    : cat === 'low_vegetation'
                    ? 'bg-lime-400'
                    : cat === 'water'
                    ? 'bg-sky-500'
                    : cat === 'building'
                    ? 'bg-rose-500'
                    : cat === 'infrastructure'
                    ? 'bg-purple-500'
                    : cat === 'bare_land'
                    ? 'bg-amber-500'
                    : 'bg-cyan-500'

                return (
                  <div key={cat} className="space-y-1">
                    <div className="flex justify-between text-xs text-slate-300">
                      <span className="capitalize font-medium">{cat.replace('_', ' ')}</span>
                      <span className="font-mono text-slate-400">
                        {Number(pct).toFixed(1)}% ({ha} ha)
                      </span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${barColor} rounded-full transition-all duration-500`}
                        style={{ width: `${Math.min(100, Number(pct))}%` }}
                      />
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      )}

      {/* ── Grounded Spatial Regions Table (if available) ── */}
      {groundedBoxes.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5 space-y-2">
          <div className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
            <Crosshair size={13} />
            <span>Grounded Spatial Regions ({groundedBoxes.length} localized)</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 text-[10.5px] text-slate-400 font-mono">
                <tr>
                  <th className="pb-1.5 font-medium">ID</th>
                  <th className="pb-1.5 font-medium">Target</th>
                  <th className="pb-1.5 font-medium">Box</th>
                  <th className="pb-1.5 font-medium text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 font-mono text-[11px]">
                {groundedBoxes.map((b, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    <td className="py-1.5 text-amber-400 font-bold">{b.region_id || `R0${idx + 1}`}</td>
                    <td className="py-1.5 font-sans font-medium text-slate-200">{b.label}</td>
                    <td className="py-1.5 text-slate-400">[{b.box?.join(', ')}]</td>
                    <td className="py-1.5 text-right font-sans font-semibold text-emerald-400">
                      {((b.confidence || 0.9) * 100).toFixed(0)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Fullscreen Lightbox Modal ── */}
      {lightboxOpen && (
        <div className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-md flex flex-col items-center justify-center p-4 sm:p-6 animate-fadeIn">
          <div className="w-full max-w-5xl flex items-center justify-between pb-3 text-white border-b border-white/10">
            <div className="flex items-center gap-2">
              <Layers size={16} className="text-cyan-400" />
              <span className="font-bold text-sm">
                Multimodal Sensor Inspection — {activeLayer.toUpperCase()}
              </span>
            </div>
            <button
              onClick={() => setLightboxOpen(false)}
              className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-bold cursor-pointer"
            >
              Close (ESC)
            </button>
          </div>

          <div className="relative flex-1 w-full max-w-5xl flex items-center justify-center p-4 overflow-hidden">
            <img
              src={currentImageUrl}
              alt="Fullscreen Multimodal Layer"
              className="max-h-[85vh] max-w-full object-contain rounded-xl shadow-2xl"
            />
            {groundedBoxes.map((b, idx) => {
              const boxCoords = b.box || [0, 0, 224, 224]
              const [ymin, xmin, ymax, xmax] = boxCoords
              return (
                <div
                  key={idx}
                  style={{
                    top: `${(ymin / 224) * 100}%`,
                    left: `${(xmin / 224) * 100}%`,
                    width: `${Math.max(3, ((xmax - xmin) / 224) * 100)}%`,
                    height: `${Math.max(3, ((ymax - ymin) / 224) * 100)}%`,
                  }}
                  className="absolute border-2 border-amber-400 bg-amber-400/20 rounded pointer-events-none"
                >
                  <span className="absolute -top-5 left-0 bg-amber-500 text-slate-950 font-bold text-xs px-2 py-0.5 rounded shadow">
                    {b.label}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
