import Header from '../components/Header'
import { UploadCloud, MessageSquareText, Layers, GitCompare } from 'lucide-react'

const faqs = [
  { icon: UploadCloud, q: 'How do I start an analysis?', a: 'Go to New Analysis, drag in a JPG, PNG or TIFF scene, then click Analyze Image. The AI detects objects and classifies land cover automatically.' },
  { icon: MessageSquareText, q: 'How does the chat assistant work?', a: 'Ask natural-language questions about the loaded scene — buildings, roads, water, vegetation — and SatQuery AI answers using the current detection results.' },
  { icon: Layers, q: 'What do the map layers do?', a: 'Toggle Buildings, Roads, Vegetation, Water or AI Detection to overlay classified regions and bounding boxes directly on the satellite image.' },
  { icon: GitCompare, q: 'How does Change Detection work?', a: 'Select two scenes of the same region captured at different times and run change detection to surface new structures, vegetation loss and road changes.' },
]

export default function Help() {
  return (
    <div className="flex-1 overflow-y-auto p-4 lg:p-6 max-w-2xl space-y-3 bg-[#f8f9fb]">
        {faqs.map((f) => (
          <div key={f.q} className="glass rounded-xl p-4 flex gap-3.5 bg-white border border-slate-200 shadow-sm">
            <div className="w-9 h-9 rounded-lg bg-sky-100 border border-sky-200 flex items-center justify-center shrink-0">
              <f.icon size={16} className="text-cyan-accent" strokeWidth={1.8} />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-800">{f.q}</p>
              <p className="text-[12.5px] text-slate-600 mt-1 leading-relaxed">{f.a}</p>
            </div>
          </div>
        ))}
      </div>
  )
}
