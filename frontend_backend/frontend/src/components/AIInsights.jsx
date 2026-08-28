import { BrainCircuit, Sparkle } from 'lucide-react'
import { aiInsights, analysisStats } from '../data/mockData'

export default function AIInsights() {
  const confidence = analysisStats.confidence
  const circumference = 2 * Math.PI * 26

  return (
    <div className="glass rounded-xl p-4 bg-white border border-slate-200 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <BrainCircuit size={16} className="text-cyan-accent" strokeWidth={1.8} />
        <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase">AI Generated Insights</p>
      </div>

      <ul className="space-y-2 mb-4">
        {aiInsights.map((insight, i) => (
          <li key={i} className="flex items-start gap-2 text-[13px] text-slate-700 leading-snug">
            <Sparkle size={11} className="text-cyan-accent mt-1 shrink-0" strokeWidth={2} />
            {insight}
          </li>
        ))}
      </ul>

      <div className="flex items-center gap-4 pt-3 border-t border-slate-200">
        <svg width="60" height="60" viewBox="0 0 60 60" className="shrink-0 -rotate-90">
          <circle cx="30" cy="30" r="26" fill="none" stroke="#e2e8f0" strokeWidth="5" />
          <circle
            cx="30"
            cy="30"
            r="26"
            fill="none"
            stroke="#0284c7"
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference * (1 - confidence / 100)}
          />
        </svg>
        <div>
          <p className="font-display text-lg font-semibold text-slate-900 leading-none">{confidence}%</p>
          <p className="text-[11px] text-slate-500 mt-1">Overall Analysis Confidence</p>
        </div>
      </div>
    </div>
  )
}
