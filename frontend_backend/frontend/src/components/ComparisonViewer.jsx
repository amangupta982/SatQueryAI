import { useState } from 'react'
import { GitCompare, Loader2, Building2, TreeDeciduous, Route } from 'lucide-react'
import { comparisonResult } from '../data/mockData'

export default function ComparisonViewer() {
  const [running, setRunning] = useState(false)
  const [done, setDone] = useState(false)

  const run = () => {
    setRunning(true)
    setTimeout(() => {
      setRunning(false)
      setDone(true)
    }, 1600)
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {[comparisonResult.imageA, comparisonResult.imageB].map((img, i) => (
          <div key={i} className="glass rounded-xl overflow-hidden">
            <div className="relative h-52">
              <img src={img.thumbnail} alt={img.filename} className="w-full h-full object-cover" />
              {done && (
                <div className="absolute inset-0 bg-signal-rose/10 mix-blend-screen pointer-events-none" />
              )}
              <span className="absolute top-2 left-2 px-2 py-0.5 rounded-md bg-base-950/80 text-[10.5px] font-mono text-cyan-soft border border-white/[0.08]">
                Image {i === 0 ? 'A' : 'B'}
              </span>
            </div>
            <div className="p-3">
              <p className="text-xs font-medium text-slate-200 truncate">{img.filename}</p>
              <p className="text-[10.5px] text-slate-500 font-mono mt-0.5">{img.date}</p>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={run}
        disabled={running}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-accent text-base-950 text-sm font-semibold hover:bg-cyan-soft transition-colors disabled:opacity-70"
      >
        {running ? <Loader2 size={15} className="animate-spin" /> : <GitCompare size={15} />}
        {running ? 'Running Change Detection…' : 'Run Change Detection'}
      </button>

      {done && (
        <div className="glass rounded-xl p-4 animate-fadeUp">
          <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase mb-3">Changes Detected</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <ChangeCard icon={Building2} label="New Structures" value={comparisonResult.newStructures} color="text-signal-amber" />
            <ChangeCard icon={TreeDeciduous} label="Vegetation-Loss Regions" value={comparisonResult.vegetationLoss} color="text-signal-rose" />
            <ChangeCard icon={Route} label="New Road Segments" value={comparisonResult.newRoadSegments} color="text-cyan-soft" />
          </div>
        </div>
      )}
    </div>
  )
}

function ChangeCard({ icon: Icon, label, value, color }) {
  return (
    <div className="rounded-lg border border-white/[0.07] bg-white/[0.02] p-3.5">
      <Icon size={16} className={`${color} mb-2`} strokeWidth={1.8} />
      <p className="font-display text-lg font-semibold text-slate-100">{value}</p>
      <p className="text-[11px] text-slate-500 mt-0.5">{label}</p>
    </div>
  )
}
