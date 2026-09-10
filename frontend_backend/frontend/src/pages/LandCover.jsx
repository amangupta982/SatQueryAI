import SceneMetaBar from '../components/SceneMetaBar'
import SatelliteViewer from '../components/SatelliteViewer'
import AnalysisStats from '../components/AnalysisStats'
import { useState } from 'react'

export default function LandCover() {
  const [layers, setLayers] = useState(['satellite', 'vegetation', 'water'])
  const toggleLayer = (key) => setLayers((prev) => (prev.includes(key) ? prev.filter((l) => l !== key) : [...prev, key]))

  return (
    <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4 bg-[#fafaf8] text-[#162721] selection:bg-[#dce7e1] selection:text-[#162721]">
      <SceneMetaBar />
      <div className="h-[420px]">
        <SatelliteViewer layers={layers} onToggleLayer={toggleLayer} />
      </div>
      <AnalysisStats />
    </div>
  )
}
