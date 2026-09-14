import { BarChart3, TrendingUp, TrendingDown, ArrowRight, Download, Layers } from 'lucide-react'

export default function ChangeStatsDashboard({
  summary,
  categories = {},
  transitions = [],
  statistics = {},
  onExportGeoJSON,
}) {
  if (!summary) return null

  const catList = Object.keys(categories).map((k) => categories[k])

  return (
    <div className="flex flex-col gap-4 bg-white p-4 rounded-xl border border-[#e5ebe7] shadow-sm text-xs">
      {/* Top Overview Cards */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-[#f6f9f7] p-3 rounded-lg border border-[#e5ebe7]">
          <span className="text-[#7a9486] font-medium block">Total Changed Area</span>
          <div className="text-xl font-bold text-[#162721] mt-0.5">
            {summary.change_percentage}%
          </div>
          <span className="text-[10px] text-[#5c7569]">
            {summary.changed_pixels.toLocaleString()} pixels
          </span>
        </div>

        <div className="bg-[#f6f9f7] p-3 rounded-lg border border-[#e5ebe7]">
          <span className="text-[#7a9486] font-medium block">Changed Regions</span>
          <div className="text-xl font-bold text-[#162721] mt-0.5">
            {statistics.region_count || 0}
          </div>
          <span className="text-[10px] text-[#5c7569]">
            Avg {statistics.average_region_pixels || 0} px/region
          </span>
        </div>

        <div className="bg-[#f6f9f7] p-3 rounded-lg border border-[#e5ebe7] flex flex-col justify-between">
          <div>
            <span className="text-[#7a9486] font-medium block">Primary Driver</span>
            <div className="text-sm font-bold text-[#162721] capitalize truncate mt-0.5">
              {summary.dominant_changed_category?.replace('_', ' ') || 'None'}
            </div>
          </div>
          <button
            onClick={onExportGeoJSON}
            className="mt-2 w-full py-1 bg-[#2d5243] hover:bg-[#223d32] text-white rounded text-[10px] font-semibold flex items-center justify-center gap-1 transition shadow-sm"
          >
            <Download size={11} />
            <span>Export GeoJSON</span>
          </button>
        </div>
      </div>

      {/* Category Breakdown Table */}
      <div className="flex flex-col gap-2 pt-2 border-t border-[#e5ebe7]">
        <div className="flex items-center gap-2 font-semibold text-[#162721]">
          <BarChart3 size={15} className="text-[#2d5243]" />
          <span>Category Area Dynamics (T1 → T2)</span>
        </div>

        <div className="flex flex-col gap-1.5 max-h-[160px] overflow-y-auto pr-1">
          {catList.map((c) => {
            const isPos = c.change_percent > 0
            const isNeg = c.change_percent < 0

            return (
              <div
                key={c.category}
                className="flex items-center justify-between p-2 rounded-lg bg-[#fbfcfb] border border-[#e5ebe7]"
              >
                <div className="flex items-center gap-2">
                  <span className="font-semibold capitalize text-[#162721]">
                    {c.category.replace('_', ' ')}
                  </span>
                  <span className="text-[10px] text-[#7a9486]">
                    ({c.t1_area_percent}% → {c.t2_area_percent}%)
                  </span>
                </div>

                <div className="flex items-center gap-1.5 font-bold">
                  {isPos && <TrendingUp size={13} className="text-emerald-600" />}
                  {isNeg && <TrendingDown size={13} className="text-rose-500" />}
                  <span className={isPos ? 'text-emerald-600' : isNeg ? 'text-rose-500' : 'text-[#7a9486]'}>
                    {isPos ? `+${c.change_percent}%` : `${c.change_percent}%`}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Land-Cover Transitions */}
      {transitions.length > 0 && (
        <div className="flex flex-col gap-2 pt-2 border-t border-[#e5ebe7]">
          <div className="flex items-center gap-2 font-semibold text-[#162721]">
            <Layers size={15} className="text-[#2d5243]" />
            <span>Top Semantic Transitions</span>
          </div>

          <div className="flex flex-col gap-1 max-h-[140px] overflow-y-auto pr-1">
            {transitions.slice(0, 5).map((t, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-1.5 rounded bg-[#f4f7f5] text-[11px]"
              >
                <div className="flex items-center gap-1.5 text-[#234238]">
                  <span className="capitalize font-medium">{t.from_category.replace('_', ' ')}</span>
                  <ArrowRight size={12} className="text-[#7a9486]" />
                  <span className="capitalize font-semibold">{t.to_category.replace('_', ' ')}</span>
                </div>
                <div className="font-semibold text-[#162721]">
                  {t.percentage}% <span className="text-[10px] text-[#7a9486]">({t.pixel_count.toLocaleString()} px)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
