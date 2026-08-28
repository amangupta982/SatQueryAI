import { useState } from 'react'
import SceneMetaBar from '../components/SceneMetaBar'
import SatelliteViewer from '../components/SatelliteViewer'
import ChatPanel from '../components/ChatPanel'
import AnalysisStats from '../components/AnalysisStats'

export default function Dashboard() {
  const [layers, setLayers] = useState(['satellite'])
  const [chatDrawerOpen, setChatDrawerOpen] = useState(false)

  const toggleLayer = (key) => {
    setLayers((prev) => (prev.includes(key) ? prev.filter((l) => l !== key) : [...prev, key]))
  }

  const activateFromChat = (key) => {
    setLayers((prev) => (prev.includes(key) ? prev : [...prev, key]))
  }

  return (
    <div className="flex-1 min-h-0 flex overflow-hidden bg-[#f8f9fb] p-4 lg:p-4 gap-4">
      {/* Center workspace */}
      <div className="flex-1 min-w-0 overflow-y-auto space-y-4 pr-1">
        {/* Scene Metadata Bar matching screenshot right after navbar */}
        <SceneMetaBar />

        {/* Satellite Map Viewer */}
        <div className="h-[380px] lg:h-[430px] w-full">
          <SatelliteViewer layers={layers} onToggleLayer={toggleLayer} />
        </div>

        {/* Summary & Land Cover Stats Cards */}
        <AnalysisStats />
      </div>

      {/* Desktop chat panel matching right column in screenshot */}
      <div className="hidden xl:block w-[380px] shrink-0 h-full">
        <ChatPanel onLayerSuggestion={activateFromChat} />
      </div>

      {/* Mobile / tablet chat drawer trigger */}
      <button
        onClick={() => setChatDrawerOpen(true)}
        className="xl:hidden fixed bottom-5 right-5 z-30 w-12 h-12 rounded-full bg-blue-600 text-white shadow-lg flex items-center justify-center font-display font-bold hover:bg-blue-700 transition-colors"
      >
        AI
      </button>

      {chatDrawerOpen && (
        <div className="xl:hidden fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-black/40" onClick={() => setChatDrawerOpen(false)} />
          <div className="relative w-full max-w-sm bg-white border-l border-slate-200 animate-fadeUp p-2">
            <button
              onClick={() => setChatDrawerOpen(false)}
              className="absolute -left-10 top-4 w-8 h-8 rounded-full bg-white border border-slate-200 text-slate-700 flex items-center justify-center shadow-md"
            >
              ✕
            </button>
            <ChatPanel onLayerSuggestion={activateFromChat} className="h-full" />
          </div>
        </div>
      )}
    </div>
  )
}
