import { Satellite, Tag } from 'lucide-react'

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end animate-fadeUp">
        <div className="max-w-[85%]">
          <div className="bg-cyan-accent/12 border border-cyan-accent/20 rounded-2xl rounded-br-sm px-3.5 py-2.5">
            <p className="text-[13px] text-slate-100 leading-snug">{message.text}</p>
          </div>
          <p className="text-[10px] text-slate-600 mt-1 text-right font-mono">{message.time}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-2 animate-fadeUp">
      <div className="w-6 h-6 rounded-full bg-cyan-accent/15 border border-cyan-accent/25 flex items-center justify-center shrink-0 mt-0.5">
        <Satellite size={11} className="text-cyan-accent" />
      </div>
      <div className="max-w-[88%] min-w-0">
        <div className="bg-white/[0.035] border border-white/[0.07] rounded-2xl rounded-tl-sm px-3.5 py-2.5">
          <p className="text-[13px] text-slate-300 leading-snug">{message.text}</p>

          {message.highlight && (
            <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-cyan-accent/10 border border-cyan-accent/20">
              <span className="text-[10.5px] text-slate-400">{message.highlight.label}</span>
              <span className="text-[12px] font-mono font-semibold text-cyan-soft">{message.highlight.value}</span>
            </div>
          )}

          {message.stats && (
            <div className="mt-2 grid grid-cols-2 gap-1.5">
              {message.stats.map((s) => (
                <div key={s.label} className="rounded-md bg-white/[0.03] border border-white/[0.06] px-2 py-1.5">
                  <p className="text-[10px] text-slate-500">{s.label}</p>
                  <p className="text-[12.5px] font-mono font-semibold text-slate-200">{s.value}</p>
                </div>
              ))}
            </div>
          )}

          {message.detectionRefs && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {message.detectionRefs.map((ref) => (
                <span
                  key={ref}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-[10.5px] text-slate-400"
                >
                  <Tag size={9} />
                  {ref}
                </span>
              ))}
            </div>
          )}
        </div>
        <p className="text-[10px] text-slate-600 mt-1 font-mono">{message.time}</p>
      </div>
    </div>
  )
}
