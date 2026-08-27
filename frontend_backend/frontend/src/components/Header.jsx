import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Menu, ChevronDown, Plus, Wifi } from 'lucide-react'
import { datasets, activeImage, userProfile } from '../data/mockData'

export default function Header({ title, status, onOpenMobileNav }) {
  const [dataset, setDataset] = useState(datasets[0])
  const [datasetOpen, setDatasetOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <header className="h-16 shrink-0 flex items-center gap-3 px-4 lg:px-6 border-b border-white/[0.06] bg-base-900/70 glass sticky top-0 z-30">
      <button
        onClick={onOpenMobileNav}
        className="lg:hidden flex items-center justify-center w-8 h-8 rounded-md text-slate-400 hover:text-slate-100 hover:bg-white/[0.06]"
      >
        <Menu size={18} />
      </button>

      <div className="min-w-0">
        <h1 className="font-display font-semibold text-[15px] text-slate-100 leading-tight truncate">{title}</h1>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="w-1.5 h-1.5 rounded-full bg-signal-lime animate-pulseSlow" />
          <p className="text-[11px] text-slate-500 truncate">{status}</p>
        </div>
      </div>

      <div className="flex-1" />

      {/* Dataset selector - hidden on small screens */}
      <div className="hidden md:block relative">
        <button
          onClick={() => setDatasetOpen((v) => !v)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] hover:bg-white/[0.06] text-xs text-slate-300"
        >
          <span className="text-slate-500">Dataset</span>
          <span className="font-medium text-slate-200">{dataset.name}</span>
          <ChevronDown size={13} className="text-slate-500" />
        </button>
        {datasetOpen && (
          <div className="absolute right-0 mt-1.5 w-56 rounded-lg border border-white/[0.08] bg-base-850 shadow-panel py-1 z-40">
            {datasets.map((d) => (
              <button
                key={d.id}
                onClick={() => {
                  setDataset(d)
                  setDatasetOpen(false)
                }}
                className={`w-full text-left px-3 py-2 text-xs hover:bg-white/[0.05] ${
                  d.id === dataset.id ? 'text-cyan-soft' : 'text-slate-300'
                }`}
              >
                {d.name}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="hidden xl:flex items-center gap-4 px-3 border-x border-white/[0.06] text-[11px] text-slate-500 font-mono">
        <span>{activeImage.acquisitionDate}</span>
        <span>{activeImage.coordinates}</span>
      </div>

      <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-signal-lime/25 bg-signal-lime/[0.06] text-[11px] text-signal-lime">
        <Wifi size={12} />
        AI Engine Online
      </div>

      <button
        onClick={() => navigate('/new-analysis')}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-accent text-base-950 text-xs font-semibold hover:bg-cyan-soft transition-colors shrink-0"
      >
        <Plus size={14} strokeWidth={2.5} />
        <span className="hidden sm:inline">New Analysis</span>
      </button>

      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-accent/40 to-base-600 border border-cyan-accent/30 flex items-center justify-center text-[11px] font-semibold text-cyan-soft shrink-0">
        {userProfile.avatarInitials}
      </div>
    </header>
  )
}
