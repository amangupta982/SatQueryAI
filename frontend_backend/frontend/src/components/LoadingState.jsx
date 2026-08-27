import { Loader2, ScanLine } from 'lucide-react'

export default function LoadingState({ label = 'Running AI vision-language analysis…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-14 text-center">
      <div className="relative w-16 h-16 mb-4">
        <div className="absolute inset-0 rounded-full border-2 border-cyan-accent/20" />
        <Loader2 size={64} strokeWidth={1.5} className="text-cyan-accent animate-spin" />
        <ScanLine size={20} strokeWidth={1.5} className="absolute inset-0 m-auto text-cyan-soft" />
      </div>
      <p className="text-sm font-medium text-slate-200">{label}</p>
      <p className="text-xs text-slate-500 mt-1 font-mono">Detecting objects · Classifying land cover · Computing confidence</p>
    </div>
  )
}
