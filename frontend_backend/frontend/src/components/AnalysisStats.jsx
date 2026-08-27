import { Boxes, Building2, Route, Droplets, Trees } from 'lucide-react'
import { analysisStats, landCoverage } from '../data/mockData'

const cards = [
  { label: 'Objects Detected', value: analysisStats.objectsDetected, icon: Boxes, accent: 'text-cyan-soft' },
  { label: 'Buildings', value: analysisStats.buildings, icon: Building2, accent: 'text-signal-amber' },
  { label: 'Roads', value: analysisStats.roads, icon: Route, accent: 'text-signal-rose' },
  { label: 'Water Bodies', value: analysisStats.waterBodies, icon: Droplets, accent: 'text-sky-400' },
  { label: 'Vegetation', value: analysisStats.vegetationAreas, icon: Trees, accent: 'text-signal-lime' },
]

export default function AnalysisStats() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {cards.map((c) => (
          <div key={c.label} className="glass rounded-xl p-3.5">
            <c.icon size={16} className={`${c.accent} mb-2`} strokeWidth={1.8} />
            <p className="font-display text-xl font-semibold text-slate-100 leading-none">{c.value}</p>
            <p className="text-[11px] text-slate-500 mt-1.5">{c.label}</p>
          </div>
        ))}
      </div>

      <div className="glass rounded-xl p-4">
        <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase mb-3">Land Coverage</p>
        <div className="space-y-2.5">
          {landCoverage.map((item) => (
            <div key={item.label}>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">{item.label}</span>
                <span className="text-slate-300 font-mono">{item.value}%</span>
              </div>
              <div className="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${item.value}%`, background: item.color }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
