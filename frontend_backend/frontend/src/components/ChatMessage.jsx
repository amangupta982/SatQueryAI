import { Sparkles, Building2, CheckCheck } from 'lucide-react'

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end animate-fadeUp">
        <div className="max-w-[88%] bg-[#eff6ff] border border-blue-100 rounded-2xl rounded-tr-xs p-3.5 shadow-xs">
          <p className="text-xs text-slate-800 leading-relaxed font-normal">{message.text}</p>
          <div className="flex items-center justify-end gap-1 mt-1 text-[10px] text-slate-400">
            <span>{message.time}</span>
            <CheckCheck size={13} className="text-blue-500" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-2.5 animate-fadeUp">
      <div className="w-6 h-6 rounded-full bg-blue-100 border border-blue-200 flex items-center justify-center shrink-0 mt-0.5 text-blue-600">
        <Sparkles size={13} />
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-3.5 shadow-xs text-xs text-slate-800">
          <div className="whitespace-pre-line leading-relaxed">{message.text}</div>
          <p className="text-[10px] text-slate-400 text-right mt-1.5 font-mono">{message.time}</p>
        </div>

        {/* Structured Card like 'Buildings Near River' in screenshot */}
        {message.card && (
          <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-xs space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
              <div className="w-5 h-5 rounded-md bg-blue-50 text-blue-600 flex items-center justify-center">
                <Building2 size={13} />
              </div>
              <span>{message.card.title}</span>
            </div>

            <div className="space-y-1.5 pt-1 text-xs">
              {message.card.stats.map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <span className="text-slate-500">{item.label}</span>
                  <span className="font-semibold text-slate-900">{item.value}</span>
                </div>
              ))}
            </div>
            <p className="text-[10px] text-slate-400 text-right pt-0.5 font-mono">{message.time}</p>
          </div>
        )}
      </div>
    </div>
  )
}
