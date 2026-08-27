import Header from '../components/Header'
import SatelliteViewer from '../components/SatelliteViewer'
import AnalysisStats from '../components/AnalysisStats'
import { useState } from 'react'

export default function LandCover({ onOpenMobileNav }) {
  const [layers, setLayers] = useState(['satellite', 'vegetation', 'water'])
  const toggleLayer = (key) => setLayers((prev) => (prev.includes(key) ? prev.filter((l) => l !== key) : [...prev, key]))

  return (
    <div className="flex flex-col h-full min-h-0">
      <Header title="Land Cover Analysis" status="Classification across 4 surface types" onOpenMobileNav={onOpenMobileNav} />
      <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-5">
        <div className="h-[420px]">
          <SatelliteViewer layers={layers} onToggleLayer={toggleLayer} />
        </div>
        <AnalysisStats />
      </div>
    </div>
  )
}
