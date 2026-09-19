import React, { useState, useEffect } from 'react'
import ChangeViewer from './ChangeViewer'
import ChangeLayerControls from './ChangeLayerControls'
import { Layers, Sliders, ChevronDown, ChevronUp, Sun, Moon, Maximize2, Minimize2 } from 'lucide-react'

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
  const [isControlsOpen, setIsControlsOpen] = useState(true)
  const [isDarkCard, setIsDarkCard] = useState(false) // Default to clean light card matching second image
  const [isFullscreen, setIsFullscreen] = useState(false)

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

  // Fullscreen keyboard handler (Esc to exit)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isFullscreen])

  // Prevent background scroll when in fullscreen
  useEffect(() => {
    if (isFullscreen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isFullscreen])

  const toggleFullscreen = () => {
    setIsFullscreen((prev) => !prev)
  }

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

  const containerClasses = isFullscreen
    ? 'fixed inset-0 z-[9999] w-screen h-screen bg-[#050b14] flex flex-col overflow-hidden p-2 sm:p-4 md:p-5 shadow-2xl backdrop-blur-2xl animate-fadeIn'
    : 'w-full my-3 rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl flex flex-col transition-all'

  return (
    <div className={containerClasses}>
      {/* Studio Header Bar */}
      <div className="px-4 py-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between flex-wrap gap-2 shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Layers size={15} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-100 tracking-wide">
                Interactive Visualization Layers Studio
              </span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-cyan-950/80 border border-cyan-500/40 text-cyan-300">
                {isFullscreen ? 'Fullscreen Mode' : 'Live Studio'}
              </span>
            </div>
            <p className="text-[10.5px] text-slate-400">
              Select any layer mode or toggle category overlays to change output in real time
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Fullscreen Toggle Button */}
          <button
            type="button"
            onClick={toggleFullscreen}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
              isFullscreen
                ? 'bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-500/40 shadow-sm'
                : 'bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 border border-cyan-500/40 shadow-sm'
            }`}
            title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'Expand to Fullscreen View'}
          >
            {isFullscreen ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
            <span>{isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}</span>
          </button>

          {/* Theme switcher between Light card (2nd image match) and Dark card */}
          <button
            type="button"
            onClick={() => setIsDarkCard(!isDarkCard)}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition cursor-pointer"
            title={isDarkCard ? 'Switch to Light Card Theme' : 'Switch to Dark Card Theme'}
          >
            {isDarkCard ? <Sun size={12} className="text-amber-400" /> : <Moon size={12} className="text-cyan-400" />}
            <span className="hidden sm:inline">{isDarkCard ? 'Light Card' : 'Dark Card'}</span>
          </button>

          <button
            type="button"
            onClick={() => setIsControlsOpen(!isControlsOpen)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
          >
            <Sliders size={13} className="text-cyan-400" />
            <span>{isControlsOpen ? 'Hide Options' : 'Show Options'}</span>
            {isControlsOpen ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>
        </div>
      </div>

      {/* Main Studio Body: Responsive Grid layout with zero clipping */}
      <div
        className={`grid grid-cols-1 md:grid-cols-12 gap-3 p-3 bg-[#0a0f12] ${
          isFullscreen ? 'flex-1 min-h-0 overflow-hidden' : ''
        }`}
      >
        {/* Left: Dual-Temporal Viewer with embedded Quick Layer Switcher */}
        <div
          className={`flex flex-col ${
            isControlsOpen
              ? isFullscreen
                ? 'md:col-span-8 lg:col-span-8 xl:col-span-9'
                : 'md:col-span-7 lg:col-span-7 xl:col-span-7'
              : 'md:col-span-12'
          } ${isFullscreen ? 'h-full min-h-0' : 'h-[460px] min-h-[380px]'}`}
        >
          <ChangeViewer
            t1Url={t1Url}
            t2Url={t2Url}
            regions={changeData.regions || []}
            selectedRegion={selectedRegion}
            onSelectRegion={setSelectedRegion}
            activeCategories={activeCategories}
            activeLayer={activeLayer}
            onChangeLayer={setActiveLayer}
            onToggleFullscreen={toggleFullscreen}
            isFullscreen={isFullscreen}
            evidenceUrls={evidenceUrls}
            palette={PALETTE}
          />
        </div>

        {/* Right: Visualization Layers & Category Overlays Panel (Matches 2nd Image) */}
        {isControlsOpen && (
          <div
            className={`${
              isFullscreen
                ? 'md:col-span-4 lg:col-span-4 xl:col-span-3 h-full'
                : 'md:col-span-5 lg:col-span-5 xl:col-span-5 h-[460px]'
            } overflow-y-auto custom-scrollbar`}
          >
            <ChangeLayerControls
              activeLayer={activeLayer}
              onChangeLayer={setActiveLayer}
              categories={effectiveCategories}
              activeCategories={activeCategories}
              onToggleCategory={handleToggleCategory}
              onSelectAllCategories={handleSelectAllCategories}
              palette={PALETTE}
              dark={isDarkCard}
            />
          </div>
        )}
      </div>

      {/* Studio Footer with active indicator */}
      <div className="px-4 py-2 bg-slate-900/60 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400 shrink-0">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Click any layer mode above to change your output view</span>
        </div>
        <div className="flex items-center gap-3 font-mono text-[10px]">
          {isFullscreen && <span className="text-slate-400">Press ESC to exit fullscreen</span>}
          <div className="text-cyan-400">
            Active Layer: <span className="capitalize font-bold text-slate-100">{activeLayer.replace('_', ' ')}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
