import Header from '../components/Header'
import { datasets } from '../data/mockData'
import { Database, ArrowUpRight } from 'lucide-react'

const meta = [
  { scenes: '1,204', region: 'Pan-India Urban' },
  { scenes: '3,880', region: 'Global Land Cover' },
  { scenes: '642', region: 'Agricultural Belts' },
  { scenes: '318', region: 'Coastal & SAR' },
]

export default function Datasets({ onOpenMobileNav }) {
  return (
    <div className="flex flex-col h-full min-h-0">
      <Header title="Datasets" status={`${datasets.length} connected sources`} onOpenMobileNav={onOpenMobileNav} />
      <div className="flex-1 overflow-y-auto p-4 lg:p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {datasets.map((d, i) => (
            <div key={d.id} className="glass rounded-xl p-4 hover:border-cyan-accent/25 border border-transparent transition-colors">
              <div className="flex items-start justify-between">
                <div className="w-9 h-9 rounded-lg bg-cyan-accent/10 border border-cyan-accent/25 flex items-center justify-center">
                  <Database size={16} className="text-cyan-accent" />
                </div>
                <ArrowUpRight size={15} className="text-slate-600" />
              </div>
              <p className="text-sm font-medium text-slate-200 mt-3">{d.name}</p>
              <div className="flex items-center gap-3 mt-1.5 text-[11px] text-slate-500 font-mono">
                <span>{meta[i].scenes} scenes</span>
                <span>·</span>
                <span>{meta[i].region}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
