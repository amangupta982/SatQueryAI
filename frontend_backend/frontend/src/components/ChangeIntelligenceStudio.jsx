import React, { useState } from 'react'
import ChangeViewer from './ChangeViewer'
import ChangeLayerControls from './ChangeLayerControls'
import { Layers, Sliders, ChevronDown, ChevronUp, Sparkles, CheckCircle2 } from 'lucide-react'

const PALETTE = {
  building: '#ff4d4d',
  vegetation: '#2ecc71',
  low_vegetation: '#a8e6cf',
  water: '#3498db',
  bare_land: '#d35400',
  infrastructure: '#9b59b6',
}

export default function ChangeIntelligenceStudio({
  changeData = {},
  imageEvidence = [],
  attachedScenes = [],
}) {
  const [activeLayer, setActiveLayer] = useState('overlay')
  const [selectedRegion, setSelectedRegion] = useState(null)

  const defaultCategories = {
    building: { change_percent: -0.77, count: 3 },
    vegetation: { change_percent: 0.40, count: 206 },
    low_vegetation: { change_percent: -1.77, count: 15 },
    water: { change_percent: -9.84, count: 98 },
    bare_land: { change_percent: 0.62, count: 72 },
    infrastructure: { change_percent: 11.39, count: 382 },
  }

  const effectiveCategories =
    changeData.categories && Object.keys(changeData.categories).length > 0
      ? changeData.categories
      : defaultCategories

  const [activeCategories, setActiveCategories] = useState(
    new Set(Object.keys(effectiveCategories))
  )
  const [isControlsOpen, setIsControlsOpen] = useState(true)

  // Build evidence URLs map
  const evidenceUrls = { ...(changeData.visualizations || {}) }
  if (imageEvidence && imageEvidence.length > 0) {
    imageEvidence.forEach((ev) => {
      if (ev.type === 'change_overlay' && !evidenceUrls.complete_overlay) {
        evidenceUrls.complete_overlay = ev.url_or_b64
      } else if (ev.type === 'change_mask' && !evidenceUrls.change_mask) {
        evidenceUrls.change_mask = ev.url_or_b64
      } else if (ev.type === 'heatmap' && !evidenceUrls.heatmap) {
        evidenceUrls.heatmap = ev.url_or_b64
      } else if (ev.type === 'diff' && !evidenceUrls.difference_image) {
        evidenceUrls.difference_image = ev.url_or_b64
      } else if (ev.type === 't2_base' && !evidenceUrls.t2_image) {
        evidenceUrls.t2_image = ev.url_or_b64
      } else if (ev.type === 't1_base' && !evidenceUrls.t1_image) {
        evidenceUrls.t1_image = ev.url_or_b64
      }
    })
  }

  // Determine T1 & T2 URLs
  const t1Url =
    changeData.t1_url ||
    evidenceUrls.t1_image ||
    (attachedScenes[0]?.preview && attachedScenes[0].preview.startsWith('data:') ? attachedScenes[0].preview : null) ||
    (attachedScenes[0]?.preview) ||
    '/satellite_scene.jpg'

  const t2Url =
    changeData.t2_url ||
    evidenceUrls.t2_image ||
    (attachedScenes[1]?.preview && attachedScenes[1].preview.startsWith('data:') ? attachedScenes[1].preview : null) ||
    (attachedScenes[1]?.preview) ||
    '/hero_brahmaputra_exact_seamless.jpg'

  const handleToggleCategory = (catName) => {
    setActiveCategories((prev) => {
      const next = new Set(prev)
      if (next.has(catName)) {
        next.delete(catName)
      } else {
        next.add(catName)
      }
      return next
    })
  }

  const handleSelectAllCategories = () => {
    const all = Object.keys(effectiveCategories)
    if (activeCategories.size === all.length) {
      setActiveCategories(new Set())
    } else {
      setActiveCategories(new Set(all))
    }
  }

  return (
    <div className="w-full my-3 rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl flex flex-col transition-all">
      {/* Studio Header Bar */}
      <div className="px-4 py-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Layers size={15} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-100 tracking-wide">
                Interactive Change Intelligence Studio
              </span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-cyan-950/80 border border-cyan-500/40 text-cyan-300">
                Live Studio
              </span>
            </div>
            <p className="text-[10.5px] text-slate-400">
              Switch layer modes, toggle category overlays, and inspect dual-temporal differences
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsControlsOpen(!isControlsOpen)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
          >
            <Sliders size={13} className="text-cyan-400" />
            <span>{isControlsOpen ? 'Hide Controls' : 'Show Controls'}</span>
            {isControlsOpen ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>
        </div>
      </div>

      {/* Main Studio Body: Viewer on Left, Layer Controls on Right */}
      <div className="flex flex-col lg:flex-row h-[520px] w-full overflow-hidden bg-[#0a0f12]">
        {/* Left: Synchronized Dual-Temporal Viewer */}
        <div className="flex-1 h-full min-h-[320px] p-2 relative">
          <ChangeViewer
            t1Url={t1Url}
            t2Url={t2Url}
            regions={changeData.regions || []}
            selectedRegion={selectedRegion}
            onSelectRegion={setSelectedRegion}
            activeCategories={activeCategories}
            activeLayer={activeLayer}
            evidenceUrls={evidenceUrls}
            palette={PALETTE}
          />
        </div>

        {/* Right: Visualization Layers & Category Overlays Panel */}
        {isControlsOpen && (
          <div className="w-full lg:w-[320px] shrink-0 h-full border-t lg:border-t-0 lg:border-l border-slate-800 overflow-y-auto p-3 animate-fadeIn custom-scrollbar">
            <ChangeLayerControls
              activeLayer={activeLayer}
              onChangeLayer={setActiveLayer}
              categories={effectiveCategories}
              activeCategories={activeCategories}
              onToggleCategory={handleToggleCategory}
              onSelectAllCategories={handleSelectAllCategories}
              palette={PALETTE}
              dark={true}
            />
          </div>
        )}
      </div>

      {/* Studio Footer with quick tips */}
      <div className="px-4 py-2 bg-slate-900/60 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Click any layer mode above to switch the viewer in real time</span>
        </div>
        <div className="font-mono text-cyan-400 text-[10px]">
          Active Mode: <span className="capitalize font-bold text-slate-100">{activeLayer.replace('_', ' ')}</span>
        </div>
      </div>
    </div>
  )
}
