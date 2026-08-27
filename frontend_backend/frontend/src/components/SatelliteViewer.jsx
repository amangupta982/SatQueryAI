import { useState } from 'react'
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize,
  Layers as LayersIcon,
  SlidersHorizontal,
  ScanEye,
} from 'lucide-react'
import { activeImage, detectionLegend } from '../data/mockData'
import DetectionOverlay from './DetectionOverlay'
import LayerControls from './LayerControls'

export default function SatelliteViewer({ layers, onToggleLayer, extraLegend }) {
  const [zoom, setZoom] = useState(100)
  const [showLayers, setShowLayers] = useState(true)
  const [fullscreen, setFullscreen] = useState(false)

  const detectionOn = layers.includes('detection')
  const activeTypes = ['buildings', 'roads', 'water', 'vegetation'].filter((t) =>
    layers.includes(t === 'buildings' ? 'buildings' : t)
  )
  // map layer keys to detection box "type" field
  const typeMap = { buildings: 'building', roads: 'road', water: 'water', vegetation: 'vegetation' }
  const activeDetectionTypes = detectionOn
    ? layers.filter((l) => typeMap[l]).map((l) => typeMap[l]).concat(layers.includes('detection') ? ['vehicle'] : [])
    : []

  return (
    <div
      className={`relative rounded-xl overflow-hidden border border-white/[0.07] bg-base-900 shadow-panel ${
        fullscreen ? 'fixed inset-3 z-50' : 'w-full h-full'
      }`}
    >
      {/* Image */}
      <div className="absolute inset-0 overflow-hidden grid-bg">
        <img
          src={activeImage.thumbnail}
          alt="Satellite scene"
          className="w-full h-full object-cover transition-transform duration-200"
          style={{ transform: `scale(${zoom / 100})` }}
          draggable={false}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-base-950/70 via-transparent to-base-950/20 pointer-events-none" />
        {detectionOn && <DetectionOverlay activeTypes={activeDetectionTypes.length ? activeDetectionTypes : ['building', 'road', 'water', 'vegetation', 'vehicle']} />}
      </div>

      {/* Scan line accent */}
      <div className="absolute inset-x-0 top-0 h-24 overflow-hidden pointer-events-none opacity-30">
        <div className="w-full h-px bg-cyan-accent/60 animate-scan" />
      </div>

      {/* Top-left controls */}
      <div className="absolute top-3 left-3 flex items-center gap-1.5 glass rounded-lg p-1">
        <ViewerBtn icon={ZoomIn} onClick={() => setZoom((z) => Math.min(z + 20, 300))} title="Zoom in" />
        <ViewerBtn icon={ZoomOut} onClick={() => setZoom((z) => Math.max(z - 20, 60))} title="Zoom out" />
        <ViewerBtn icon={RotateCcw} onClick={() => setZoom(100)} title="Reset" />
        <ViewerBtn icon={Maximize} onClick={() => setFullscreen((v) => !v)} title="Fullscreen" />
      </div>

      {/* Top-right controls */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5">
        <div className="glass rounded-lg p-1 flex items-center gap-1">
          <ViewerBtn icon={LayersIcon} onClick={() => setShowLayers((v) => !v)} title="Layers" active={showLayers} />
          <ViewerBtn icon={SlidersHorizontal} title="Image settings" />
          <ViewerBtn icon={ScanEye} onClick={() => onToggleLayer('detection')} title="Detection overlay" active={detectionOn} />
        </div>
      </div>

      {/* Layers panel */}
      {showLayers && (
        <div className="absolute top-16 right-3 z-10">
          <LayerControls layers={layers} onToggle={onToggleLayer} />
        </div>
      )}

      {/* Legend */}
      {detectionOn && (
        <div className="absolute bottom-14 left-3 glass rounded-lg px-3 py-2.5 z-10">
          <p className="text-[10px] font-semibold tracking-wider text-slate-500 uppercase mb-1.5">AI Detection</p>
          <div className="space-y-1">
            {(extraLegend || detectionLegend).map((item) => (
              <div key={item.type} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-sm" style={{ background: item.color }} />
                <span className="text-[11px] text-slate-400">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bottom status bar */}
      <div className="absolute bottom-0 inset-x-0 h-9 flex items-center justify-between px-3.5 bg-base-950/80 border-t border-white/[0.06] text-[10.5px] font-mono text-slate-500">
        <span>{activeImage.coordinates}</span>
        <div className="hidden sm:flex items-center gap-4">
          <span>Zoom {zoom}%</span>
          <span>{activeImage.resolution}</span>
          <span>{activeImage.acquisitionDate}</span>
        </div>
      </div>

      {fullscreen && (
        <button
          onClick={() => setFullscreen(false)}
          className="absolute top-3 right-3 z-20 hidden"
        />
      )}
    </div>
  )
}

function ViewerBtn({ icon: Icon, onClick, title, active }) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={`flex items-center justify-center w-7 h-7 rounded-md transition-colors ${
        active ? 'bg-cyan-accent/20 text-cyan-soft' : 'text-slate-400 hover:text-slate-100 hover:bg-white/[0.08]'
      }`}
    >
      <Icon size={14} strokeWidth={1.9} />
    </button>
  )
}
