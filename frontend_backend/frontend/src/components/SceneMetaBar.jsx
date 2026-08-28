import { useState } from 'react'
import { ChevronDown, Calendar, Crosshair, MapPin, Layers } from 'lucide-react'
import { datasets, activeImage } from '../data/mockData'

export default function SceneMetaBar() {
  const [dataset, setDataset] = useState(datasets[0])
  const [datasetOpen, setDatasetOpen] = useState(false)

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center gap-4 sm:gap-6 bg-white border border-slate-200/90 rounded-2xl px-4 py-2.5 text-xs text-slate-700 shadow-xs">
        {/* Dataset selector */}
        <div className="relative">
          <button
            onClick={() => setDatasetOpen((v) => !v)}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 font-bold text-slate-800 transition-colors shadow-2xs"
          >
            <Layers size={15} className="text-slate-700" strokeWidth={2} />
            <span>{dataset.name}</span>
            <ChevronDown size={13} className="text-slate-400" />
          </button>

          {datasetOpen && (
            <div className="absolute left-0 mt-1.5 w-60 rounded-xl border border-slate-200 bg-white shadow-lg py-1 z-40">
              {datasets.map((d) => (
                <button
                  key={d.id}
                  onClick={() => {
                    setDataset(d)
                    setDatasetOpen(false)
                  }}
                  className={`w-full text-left px-3.5 py-2 text-xs hover:bg-slate-50 flex items-center justify-between ${
                    d.id === dataset.id ? 'text-blue-600 font-bold bg-blue-50/60' : 'text-slate-700'
                  }`}
                >
                  <span>{d.name}</span>
                  {d.id === dataset.id && <span className="text-blue-600 font-bold">✓</span>}
                </button>
              ))}
            </div>
          )}
        </div>

        <span className="hidden sm:inline text-slate-200 text-sm">|</span>

        {/* Acquisition Date */}
        <div className="flex items-center gap-2 text-slate-700 font-medium">
          <Calendar size={15} className="text-slate-600" strokeWidth={2} />
          <span className="font-semibold text-slate-800">{activeImage.acquisitionDate}</span>
        </div>

        <span className="hidden sm:inline text-slate-200 text-sm">|</span>

        {/* Resolution */}
        <div className="flex items-center gap-2 text-slate-700 font-medium font-mono">
          <Crosshair size={15} className="text-slate-600" strokeWidth={2} />
          <span className="font-semibold text-slate-800">{activeImage.resolution}</span>
        </div>

        <span className="hidden sm:inline text-slate-200 text-sm">|</span>

        {/* Coordinates */}
        <div className="flex items-center gap-2 text-slate-700 font-medium font-mono">
          <MapPin size={15} className="text-slate-600" strokeWidth={2} />
          <span className="font-semibold text-slate-800">{activeImage.coordinates}</span>
        </div>
      </div>
    </div>
  )
}
