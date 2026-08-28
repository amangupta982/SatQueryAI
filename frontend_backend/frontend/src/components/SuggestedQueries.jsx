import { Milestone, Leaf, Droplet, GitCompare } from 'lucide-react'
import { suggestedQueries } from '../data/mockData'

const icons = {
  road: Milestone,
  vegetation: Leaf,
  water: Droplet,
  compare: GitCompare,
}

export default function SuggestedQueries({ onSelect }) {
  return (
    <div className="space-y-1.5 px-3.5 pb-3">
      {suggestedQueries.map((q) => {
        const Icon = icons[q.type] || Milestone
        return (
          <button
            key={q.text}
            onClick={() => onSelect(q.text)}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl border border-slate-200 bg-white text-xs text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-colors text-left shadow-xs"
          >
            <Icon size={14} className="text-slate-500 shrink-0" strokeWidth={1.8} />
            <span className="truncate">{q.text}</span>
          </button>
        )
      })}
    </div>
  )
}
