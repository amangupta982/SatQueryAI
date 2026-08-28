import { LayoutGrid, Building2, Milestone, Droplet, Leaf, Info } from 'lucide-react'
import { analysisStats, landCoverage } from '../data/mockData'

const stats = [
  {
    icon: LayoutGrid,
    value: analysisStats.objectsDetected,
    label: 'Objects Detected',
    iconBg: 'bg-blue-50',
    iconColor: 'text-blue-600',
  },
  {
    icon: Building2,
    value: analysisStats.buildings,
    label: 'Buildings',
    iconBg: 'bg-emerald-50',
    iconColor: 'text-emerald-600',
  },
  {
    icon: Milestone,
    value: analysisStats.roads,
    label: 'Roads',
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
  },
  {
    icon: Droplet,
    value: analysisStats.waterBodies,
    label: 'Water Bodies',
    iconBg: 'bg-sky-50',
    iconColor: 'text-sky-600',
  },
  {
    icon: Leaf,
    value: analysisStats.vegetationAreas,
    label: 'Vegetation Areas',
    iconBg: 'bg-green-50',
    iconColor: 'text-green-600',
  },
]

export default function AnalysisStats() {
  return (
    <div className="space-y-4">
      {/* Summary Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 mb-4">Summary</h3>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 divide-y sm:divide-y-0 sm:divide-x divide-slate-100">
          {stats.map((s, i) => (
            <div
              key={s.label}
              className={`flex items-center gap-3.5 ${i > 0 ? 'sm:pl-4' : ''} ${i > 0 ? 'pt-2 sm:pt-0' : ''}`}
            >
              <div
                className={`w-10 h-10 rounded-xl ${s.iconBg} ${s.iconColor} flex items-center justify-center shrink-0 border border-slate-100 shadow-2xs`}
              >
                <s.icon size={19} strokeWidth={2} />
              </div>
              <div className="min-w-0">
                <p className="font-display text-lg font-bold text-slate-900 leading-none">{s.value}</p>
                <p className="text-xs text-slate-500 font-medium mt-1 truncate">{s.label}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Land Cover (AI Classification) Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
        <div className="flex items-center gap-1.5 mb-3.5">
          <h3 className="text-sm font-bold text-slate-900">Land Cover (AI Classification)</h3>
          <Info size={14} className="text-slate-400 cursor-pointer hover:text-slate-600 transition-colors" />
        </div>

        {/* Continuous Segmented Bar */}
        <div className="h-3.5 rounded-full overflow-hidden flex w-full bg-slate-100 mb-4 shadow-inner">
          {landCoverage.map((item) => (
            <div
              key={item.label}
              className="h-full transition-all duration-500 first:rounded-l-full last:rounded-r-full"
              style={{ width: `${item.value}%`, backgroundColor: item.color }}
              title={`${item.label}: ${item.value}%`}
            />
          ))}
        </div>

        {/* Legend row with exact spacing */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs text-slate-700 pt-1">
          {landCoverage.map((item) => (
            <div key={item.label} className="flex items-center justify-between sm:justify-start gap-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                <span className="text-slate-700 font-medium text-xs">{item.label}</span>
              </div>
              <span className="font-bold text-slate-900 font-mono text-xs">{item.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
