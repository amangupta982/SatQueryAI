import { Layers, Eye, EyeOff, Info } from 'lucide-react'

export default function ChangeLayerControls({
  activeLayer,
  onChangeLayer,
  categories = {},
  activeCategories,
  onToggleCategory,
  onSelectAllCategories,
  palette = {},
  legend = {},
}) {
  const layerOptions = [
    { id: 'overlay', label: 'Complete Overlay', desc: 'All detected changes blended onto T2' },
    { id: 'heatmap', label: 'Change Heatmap', desc: 'Continuous change intensity gradient' },
    { id: 'mask', label: 'Binary Mask', desc: 'Per-pixel change (white) vs no-change' },
    { id: 'diff', label: 'Raw Difference', desc: 'Radiometric band-difference image' },
    { id: 't2_only', label: 'T2 Base Image', desc: 'Original unaltered later image' },
  ]

  const catList = Object.keys(categories).map((k) => ({
    name: k,
    stats: categories[k],
    color: palette[k] || '#808080',
  }))

  return (
    <div className="flex flex-col gap-4 bg-white p-4 rounded-xl border border-[#e5ebe7] shadow-sm text-sm">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[#e5ebe7]">
        <div className="flex items-center gap-2 font-semibold text-[#162721]">
          <Layers size={16} className="text-[#2d5243]" />
          <span>Visualization Layers</span>
        </div>
      </div>

      {/* Layer selector */}
      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-medium text-[#5c7569] uppercase tracking-wider">Active Layer Mode</label>
        <div className="grid grid-cols-1 gap-1">
          {layerOptions.map((opt) => (
            <button
              key={opt.id}
              onClick={() => onChangeLayer(opt.id)}
              className={`px-3 py-2 rounded-lg text-left transition flex flex-col ${
                activeLayer === opt.id
                  ? 'bg-[#2d5243] text-white shadow-sm'
                  : 'hover:bg-[#f2f6f4] text-[#162721]'
              }`}
            >
              <span className="font-medium text-xs">{opt.label}</span>
              <span className={`text-[10px] ${activeLayer === opt.id ? 'text-[#a4baa9]' : 'text-[#7a9486]'}`}>
                {opt.desc}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Category Toggles */}
      <div className="flex flex-col gap-2 pt-2 border-t border-[#e5ebe7]">
        <div className="flex items-center justify-between">
          <label className="text-xs font-medium text-[#5c7569] uppercase tracking-wider">Category Overlays</label>
          <button
            onClick={onSelectAllCategories}
            className="text-[11px] text-[#2d5243] hover:underline font-medium"
          >
            Toggle All
          </button>
        </div>

        <div className="flex flex-col gap-1 max-h-[180px] overflow-y-auto pr-1">
          {catList.map((cat) => {
            const isChecked = activeCategories.has(cat.name)
            return (
              <label
                key={cat.name}
                className="flex items-center justify-between p-1.5 rounded hover:bg-[#f6f9f7] cursor-pointer transition select-none"
              >
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => onToggleCategory(cat.name)}
                    className="rounded border-[#a4baa9] text-[#2d5243] focus:ring-[#2d5243]"
                  />
                  <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: cat.color }} />
                  <span className="text-xs font-medium capitalize text-[#162721]">{cat.name.replace('_', ' ')}</span>
                </div>
                <div className="text-[11px] text-[#5c7569]">
                  {cat.stats?.change_percent > 0 ? `+${cat.stats.change_percent}%` : `${cat.stats?.change_percent || 0}%`}
                </div>
              </label>
            )
          })}
        </div>
      </div>

      {/* Visual Legend */}
      <div className="pt-2 border-t border-[#e5ebe7] flex flex-col gap-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-[#162721]">
          <Info size={13} className="text-[#5c7569]" />
          <span>Visual Legend & Interpretation</span>
        </div>
        <div className="bg-[#f9faf9] p-2.5 rounded-lg border border-[#e5ebe7] text-[11px] text-[#4d665a] flex flex-col gap-1.5">
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 border-2 border-[#ff4d4d] rounded-sm bg-[#ff4d4d]/20 shrink-0" />
            <span>Bounding Box: Localized change region boundary</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-white border border-black shrink-0" />
            <span>Center Marker: Region spatial centroid</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-8 h-2 rounded bg-gradient-to-r from-blue-500 via-green-400 to-red-500 shrink-0" />
            <span>Heatmap: Low (Blue) to High (Red) change intensity</span>
          </div>
        </div>
      </div>
    </div>
  )
}
