import { useState, useRef, useEffect } from 'react'
import { ZoomIn, ZoomOut, RotateCcw, Split, Columns } from 'lucide-react'

export default function ChangeViewer({
  t1Url,
  t2Url,
  regions = [],
  selectedRegion = null,
  onSelectRegion = () => {},
  activeCategories = new Set(),
  activeLayer = 'overlay', // 'overlay', 'heatmap', 'mask', 'diff', 't2_only'
  evidenceUrls = {},
  palette = {},
}) {
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [viewMode, setViewMode] = useState('side_by_side') // 'side_by_side' or 'split_slider'
  const [splitPos, setSplitPos] = useState(50)

  const containerRef = useRef(null)

  const handleMouseDown = (e) => {
    if (e.button === 0) {
      setIsDragging(true)
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
    }
  }

  const handleMouseMove = (e) => {
    if (!isDragging) return
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y })
  }

  const handleMouseUp = () => setIsDragging(false)

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.25, 4))
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.5))
  const handleReset = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  // Filter visible regions by active categories
  const visibleRegions = regions.filter((r) => {
    if (activeCategories.size === 0) return true
    return activeCategories.has(r.category)
  })

  // Determine which image to show on the "After/T2" side based on active layer
  const getRightImageSrc = () => {
    if (activeLayer === 'heatmap' && evidenceUrls.heatmap) return evidenceUrls.heatmap
    if (activeLayer === 'mask' && evidenceUrls.change_mask) return evidenceUrls.change_mask
    if (activeLayer === 'diff' && evidenceUrls.difference_image) return evidenceUrls.difference_image
    if (activeLayer === 'overlay' && evidenceUrls.complete_overlay) return evidenceUrls.complete_overlay
    return t2Url
  }

  return (
    <div className="flex flex-col h-full w-full bg-[#111915] rounded-xl overflow-hidden border border-[#2a3d34] select-none">
      {/* Top Toolbar */}
      <div className="h-11 px-4 bg-[#162721] border-b border-[#2a3d34] flex items-center justify-between text-xs text-[#a4baa9]">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-white uppercase tracking-wider">Synchronized Dual-Temporal Viewer</span>
          <span className="bg-[#223d32] px-2 py-0.5 rounded text-[10px] text-[#71dd94] border border-[#2d5243]">
            {zoom.toFixed(2)}x
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setViewMode(viewMode === 'side_by_side' ? 'split_slider' : 'side_by_side')}
            className={`p-1.5 rounded transition ${viewMode === 'split_slider' ? 'bg-[#2d5243] text-white' : 'hover:bg-[#1f362c] text-[#a4baa9]'}`}
            title="Toggle Split Slider Mode"
          >
            {viewMode === 'side_by_side' ? <Split size={15} /> : <Columns size={15} />}
          </button>
          <div className="h-4 w-px bg-[#2a3d34] mx-1" />
          <button onClick={handleZoomIn} className="p-1.5 rounded hover:bg-[#1f362c] text-white" title="Zoom In">
            <ZoomIn size={15} />
          </button>
          <button onClick={handleZoomOut} className="p-1.5 rounded hover:bg-[#1f362c] text-white" title="Zoom Out">
            <ZoomOut size={15} />
          </button>
          <button onClick={handleReset} className="p-1.5 rounded hover:bg-[#1f362c] text-[#a4baa9]" title="Reset View">
            <RotateCcw size={15} />
          </button>
        </div>
      </div>

      {/* Main Canvas Area */}
      <div
        ref={containerRef}
        className="relative flex-1 w-full h-full overflow-hidden cursor-grab active:cursor-grabbing flex"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {viewMode === 'side_by_side' ? (
          <div className="flex w-full h-full">
            {/* Left: T1 (Earlier) */}
            <div className="relative flex-1 h-full border-r border-[#2a3d34] overflow-hidden flex items-center justify-center bg-[#0d1411]">
              <div className="absolute top-3 left-3 z-10 bg-[#162721]/80 backdrop-blur px-2.5 py-1 rounded text-xs font-semibold text-white border border-[#2d5243]">
                T1: Earlier Acquisition
              </div>
              <div
                style={{
                  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                  transformOrigin: 'center center',
                  transition: isDragging ? 'none' : 'transform 0.1s ease-out',
                }}
                className="relative max-w-full max-h-full"
              >
                {t1Url ? (
                  <img src={t1Url} alt="T1 Reference" className="max-w-none w-[512px] h-[512px] object-contain pointer-events-none" />
                ) : (
                  <div className="w-[400px] h-[400px] flex items-center justify-center text-[#527163] border border-dashed border-[#2a3d34] rounded">
                    No T1 image uploaded
                  </div>
                )}
              </div>
            </div>

            {/* Right: T2 (Later) + Overlays */}
            <div className="relative flex-1 h-full overflow-hidden flex items-center justify-center bg-[#0d1411]">
              <div className="absolute top-3 left-3 z-10 bg-[#162721]/80 backdrop-blur px-2.5 py-1 rounded text-xs font-semibold text-white border border-[#2d5243] flex items-center gap-2">
                <span>T2: Later Acquisition</span>
                <span className="text-[10px] text-[#71dd94] capitalize">({activeLayer})</span>
              </div>
              <div
                style={{
                  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                  transformOrigin: 'center center',
                  transition: isDragging ? 'none' : 'transform 0.1s ease-out',
                }}
                className="relative max-w-full max-h-full"
              >
                {getRightImageSrc() ? (
                  <img src={getRightImageSrc()} alt="T2 Current" className="max-w-none w-[512px] h-[512px] object-contain pointer-events-none" />
                ) : (
                  <div className="w-[400px] h-[400px] flex items-center justify-center text-[#527163] border border-dashed border-[#2a3d34] rounded">
                    No T2 image uploaded
                  </div>
                )}

                {/* Interactive SVG Bounding Box and Region Overlays */}
                <svg className="absolute inset-0 w-full h-full pointer-events-auto" viewBox="0 0 512 512">
                  {visibleRegions.map((reg) => {
                    const [xmin, ymin, xmax, ymax] = reg.bbox
                    const isSelected = selectedRegion?.region_id === reg.region_id
                    const color = palette[reg.category] || '#ff4d4d'

                    return (
                      <g key={reg.region_id} onClick={(e) => { e.stopPropagation(); onSelectRegion(reg); }} className="cursor-pointer group">
                        {/* Bounding Box */}
                        <rect
                          x={xmin}
                          y={ymin}
                          width={Math.max(4, xmax - xmin)}
                          height={Math.max(4, ymax - ymin)}
                          fill={isSelected ? `${color}33` : 'transparent'}
                          stroke={isSelected ? '#ffff00' : color}
                          strokeWidth={isSelected ? 3 : 2}
                          strokeDasharray={isSelected ? '4,4' : 'none'}
                          className="transition-all hover:stroke-white hover:stroke-[3px]"
                        />

                        {/* Centroid Pin */}
                        <circle
                          cx={reg.centroid_pixel[0]}
                          cy={reg.centroid_pixel[1]}
                          r={isSelected ? 5 : 3}
                          fill={isSelected ? '#ffff00' : '#ffffff'}
                          stroke={color}
                          strokeWidth={2}
                        />

                        {/* Region Tag */}
                        <text
                          x={xmin}
                          y={Math.max(12, ymin - 4)}
                          fill="#ffffff"
                          fontSize="10"
                          fontWeight="bold"
                          className="drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)] pointer-events-none"
                        >
                          {reg.region_id}
                        </text>
                      </g>
                    )
                  })}
                </svg>
              </div>
            </div>
          </div>
        ) : (
          /* Split Slider Mode */
          <div className="relative w-full h-full flex items-center justify-center bg-[#0d1411]">
            <div
              style={{
                transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                transformOrigin: 'center center',
              }}
              className="relative w-[512px] h-[512px]"
            >
              {/* Underneath: T2 image */}
              <img src={getRightImageSrc() || t2Url} alt="T2" className="absolute inset-0 w-full h-full object-contain pointer-events-none" />

              {/* On top: T1 image with clip path */}
              <div
                className="absolute inset-0 overflow-hidden"
                style={{ clipPath: `polygon(0 0, ${splitPos}% 0, ${splitPos}% 100%, 0 100%)` }}
              >
                <img src={t1Url} alt="T1" className="absolute inset-0 w-full h-full object-contain pointer-events-none" />
              </div>

              {/* Slider bar */}
              <div
                className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize shadow-[0_0_8px_rgba(0,0,0,0.8)] z-20 flex items-center justify-center"
                style={{ left: `${splitPos}%` }}
              >
                <div className="w-5 h-5 rounded-full bg-white text-[#111915] flex items-center justify-center text-[10px] font-bold shadow">
                  ↔
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
