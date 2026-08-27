import { useState } from 'react'
import Header from '../components/Header'
import SatelliteViewer from '../components/SatelliteViewer'
import ChatPanel from '../components/ChatPanel'
import AnalysisStats from '../components/AnalysisStats'
import AIInsights from '../components/AIInsights'

export default function Dashboard({ onOpenMobileNav }) {
  const [layers, setLayers] = useState(['satellite'])
  const [chatDrawerOpen, setChatDrawerOpen] = useState(false)

  const toggleLayer = (key) => {
    setLayers((prev) => (prev.includes(key) ? prev.filter((l) => l !== key) : [...prev, key]))
  }

  const activateFromChat = (key) => {
    setLayers((prev) => (prev.includes(key) ? prev : [...prev, key]))
  }

  return (
    <div className="flex flex-col h-full min-h-0">
      <Header title="Satellite Analysis" status="AI Analysis Ready" onOpenMobileNav={onOpenMobileNav} />

      <div className="flex-1 min-h-0 flex overflow-hidden">
        {/* Center workspace */}
        <div className="flex-1 min-w-0 overflow-y-auto p-4 lg:p-5 space-y-5">
          <div className="h-[420px] lg:h-[480px]">
            <SatelliteViewer layers={layers} onToggleLayer={toggleLayer} />
          </div>
          <AnalysisStats />
          <AIInsights />
        </div>

        {/* Desktop chat panel */}
        <div className="hidden xl:block w-[360px] shrink-0 border-l border-white/[0.06]">
          <ChatPanel onLayerSuggestion={activateFromChat} />
        </div>
      </div>

      {/* Mobile / tablet chat drawer trigger */}
      <button
        onClick={() => setChatDrawerOpen(true)}
        className="xl:hidden fixed bottom-5 right-5 z-30 w-12 h-12 rounded-full bg-cyan-accent text-base-950 shadow-glow flex items-center justify-center font-display font-bold"
      >
        AI
      </button>

      {chatDrawerOpen && (
        <div className="xl:hidden fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-black/60" onClick={() => setChatDrawerOpen(false)} />
          <div className="relative w-full max-w-sm bg-base-900 border-l border-white/[0.08] animate-fadeUp">
            <button
              onClick={() => setChatDrawerOpen(false)}
              className="absolute -left-10 top-4 w-8 h-8 rounded-full bg-base-900 border border-white/[0.1] text-slate-300 flex items-center justify-center"
            >
              ✕
            </button>
            <ChatPanel onLayerSuggestion={activateFromChat} className="h-screen" />
          </div>
        </div>
      )}
    </div>
  )
}
