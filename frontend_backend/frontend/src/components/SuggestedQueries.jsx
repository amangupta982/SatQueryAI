import { suggestedQueries } from '../data/mockData'

export default function SuggestedQueries({ onSelect }) {
  return (
    <div className="flex flex-wrap gap-1.5 px-4 pb-2.5">
      {suggestedQueries.map((q) => (
        <button
          key={q}
          onClick={() => onSelect(q)}
          className="px-2.5 py-1 rounded-full border border-white/[0.09] text-[11px] text-slate-400 hover:text-cyan-soft hover:border-cyan-accent/30 hover:bg-cyan-accent/[0.06] transition-colors"
        >
          {q}
        </button>
      ))}
    </div>
  )
}
