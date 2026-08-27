import { useState } from 'react'
import Header from '../components/Header'
import ImageUploader from '../components/ImageUploader'
import SatelliteViewer from '../components/SatelliteViewer'
import ChatPanel from '../components/ChatPanel'
import AnalysisStats from '../components/AnalysisStats'
import AIInsights from '../components/AIInsights'
import LoadingState from '../components/LoadingState'
import { CheckCircle2 } from 'lucide-react'

export default function NewAnalysis({ onOpenMobileNav }) {
  const [stage, setStage] = useState('upload') // upload -> processing -> results
  const [layers, setLayers] = useState(['satellite', 'detection'])

  const toggleLayer = (key) => {
    setLayers((prev) => (prev.includes(key) ? prev.filter((l) => l !== key) : [...prev, key]))
  }
  const activateFromChat = (key) => {
    setLayers((prev) => (prev.includes(key) ? prev : [...prev, key]))
  }

  const handleAnalyze = () => {
    setStage('processing')
    setTimeout(() => setStage('results'), 1900)
  }

  return (
    <div className="flex flex-col h-full min-h-0">
      <Header title="New Analysis" status="Step 1 of 2 · Upload an image" onOpenMobileNav={onOpenMobileNav} />

      <div className="flex-1 min-h-0 flex overflow-hidden">
        <div className="flex-1 min-w-0 overflow-y-auto p-4 lg:p-6">
          {stage === 'upload' && (
            <div className="max-w-2xl mx-auto mt-4">
              <ImageUploader onAnalyze={handleAnalyze} />
              <div className="mt-6 grid grid-cols-3 gap-3 text-center">
                <StepChip n={1} label="Upload" active />
                <StepChip n={2} label="Analyze" />
                <StepChip n={3} label="Explore" />
              </div>
            </div>
          )}

          {stage === 'processing' && (
            <div className="max-w-2xl mx-auto mt-10">
              <LoadingState />
            </div>
          )}

          {stage === 'results' && (
            <div className="space-y-5 animate-fadeUp">
              <div className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-signal-lime/[0.07] border border-signal-lime/25 text-signal-lime text-xs w-fit">
                <CheckCircle2 size={14} /> Analysis complete — 42 objects detected
              </div>
              <div className="h-[420px] lg:h-[460px]">
                <SatelliteViewer layers={layers} onToggleLayer={toggleLayer} />
              </div>
              <AnalysisStats />
              <AIInsights />
            </div>
          )}
        </div>

        <div className="hidden xl:block w-[360px] shrink-0 border-l border-white/[0.06]">
          <ChatPanel onLayerSuggestion={activateFromChat} />
        </div>
      </div>
    </div>
  )
}

function StepChip({ n, label, active }) {
  return (
    <div
      className={`rounded-lg border px-3 py-2.5 ${
        active ? 'border-cyan-accent/30 bg-cyan-accent/[0.06]' : 'border-white/[0.07] bg-white/[0.015]'
      }`}
    >
      <p className={`font-display text-sm font-semibold ${active ? 'text-cyan-soft' : 'text-slate-600'}`}>{n}</p>
      <p className={`text-[11px] mt-0.5 ${active ? 'text-slate-300' : 'text-slate-600'}`}>{label}</p>
    </div>
  )
}
