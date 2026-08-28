import { Check } from 'lucide-react'

const LAYERS = [
  { key: 'satellite', label: 'Satellite Image', locked: true },
  { key: 'buildings', label: 'Buildings' },
  { key: 'roads', label: 'Roads' },
  { key: 'vegetation', label: 'Vegetation' },
  { key: 'water', label: 'Water' },
  { key: 'detection', label: 'AI Detection' },
]

export default function LayerControls({ layers, onToggle }) {
  return (
    <div className="glass rounded-xl p-3.5 w-48 shadow-lg bg-white/95 border border-slate-200">
      <p className="text-[10.5px] font-semibold tracking-wider text-slate-500 uppercase mb-2">Layers</p>
      <div className="space-y-1.5">
        {LAYERS.map((l) => {
          const active = l.locked || layers.includes(l.key)
          return (
            <button
              key={l.key}
              disabled={l.locked}
              onClick={() => onToggle(l.key)}
              className="flex items-center gap-2 w-full text-left group disabled:cursor-default"
            >
              <span
                className={`flex items-center justify-center w-4 h-4 rounded border shrink-0 transition-colors ${
                  active
                    ? 'bg-cyan-accent border-cyan-accent text-white'
                    : 'border-slate-300 bg-white group-hover:border-slate-400'
                }`}
              >
                {active && <Check size={11} strokeWidth={3} className="text-white" />}
              </span>
              <span className={`text-xs ${active ? 'text-slate-800 font-medium' : 'text-slate-500'}`}>{l.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
