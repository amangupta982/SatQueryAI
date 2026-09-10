import { useState } from 'react'
import SceneMetaBar from '../components/SceneMetaBar'
import SatelliteViewer from '../components/SatelliteViewer'
import { detectionTypes, detectionBoxes } from '../data/mockData'
import { Loader2, Play } from 'lucide-react'

export default function Detection() {
  const [selected, setSelected] = useState(['Buildings'])
  const [running, setRunning] = useState(false)
  const [ran, setRan] = useState(false)
  const [layers, setLayers] = useState(['satellite'])

  const toggle = (t) => setSelected((s) => (s.includes(t) ? s.filter((x) => x !== t) : [...s, t]))
  const toggleLayer = (key) => setLayers((prev) => (prev.includes(key) ? prev.filter((l) => l !== key) : [...prev, key]))

  const run = () => {
    setRunning(true)
    setTimeout(() => {
      setRunning(false)
      setRan(true)
      setLayers(['satellite', 'detection'])
    }, 1600)
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4 bg-[#fafaf8] text-[#162721] selection:bg-[#dce7e1] selection:text-[#162721]">
      <SceneMetaBar />
        <div className="glass rounded-xl p-4 bg-white border border-[#e5ebe7] shadow-sm">
          <p className="text-[11px] font-semibold tracking-wider text-[#5f7168] uppercase mb-3">Detection Type</p>
          <div className="flex flex-wrap gap-2 mb-4">
            {detectionTypes.map((t) => (
              <button
                key={t}
                onClick={() => toggle(t)}
                className={`px-3 py-1.5 rounded-lg border text-xs transition-colors shadow-sm ${
                  selected.includes(t)
                    ? 'border-[#c8d4ce] bg-[#e2eae5] text-[#234238] font-semibold'
                    : 'border-[#d8e0dc] bg-white text-slate-600 hover:text-[#162721] hover:bg-[#f2f6f4]'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
          <button
            onClick={run}
            disabled={running}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#234238] text-white text-sm font-semibold hover:bg-[#1a342c] transition-colors disabled:opacity-70 shadow-sm"
          >
            {running ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}
            {running ? 'Running Detection…' : 'Run Detection'}
          </button>
        </div>

        <div className="h-[420px]">
          <SatelliteViewer layers={layers} onToggleLayer={toggleLayer} />
        </div>

        {ran && (
          <div className="glass rounded-xl p-4 animate-fadeUp bg-white border border-[#e5ebe7] shadow-sm">
            <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase mb-3">Detected Objects</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
              {detectionBoxes.map((b) => (
                <div key={b.id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p className="text-sm font-medium text-slate-800">{b.label}</p>
                  <p className="text-[11px] text-slate-500 mt-0.5 font-mono">Confidence: {b.confidence}%</p>
                  <p className="text-[10.5px] text-slate-400 mt-1 font-mono">x:{b.x}% y:{b.y}%</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
  )
}
