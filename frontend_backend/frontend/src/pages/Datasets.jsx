import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Database,
  Search,
  Layers,
  Sparkles,
  ArrowRight,
  Radio,
  Satellite,
  Globe,
  Sliders,
  CheckCircle2,
  Calendar,
  Eye,
} from 'lucide-react'
import { eoDatasetsCatalog } from '../data/mockData'

export default function Datasets() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedModality, setSelectedModality] = useState('All')

  const modalities = ['All', 'Multispectral Optical', 'Very High-Resolution Optical', 'SAR']

  const filteredDatasets = eoDatasetsCatalog.filter((ds) => {
    const matchesQuery =
      ds.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ds.agency.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ds.modality.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ds.applications.some((app) => app.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesModality =
      selectedModality === 'All' || ds.modality.toLowerCase().includes(selectedModality.toLowerCase())

    return matchesQuery && matchesModality
  })

  const handleQuickAnalyze = (dataset) => {
    navigate('/new-analysis', {
      state: {
        presetSensor: dataset.name,
      },
    })
  }

  return (
    <div className="flex-1 overflow-y-auto bg-[#fafaf8] px-4 py-6 md:px-8 lg:px-12 text-[#162721] selection:bg-[#dce7e1] selection:text-[#162721]">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header section */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-[11px] font-semibold tracking-wider text-[#234238] mb-1">
              <Database size={13} className="text-[#234238]" />
              <span>EARTH OBSERVATION DATA REPOSITORY</span>
              <span className="text-slate-300">/</span>
              <span className="text-[#5f7168] font-normal">Constellation Catalog</span>
            </div>

            <h1 className="text-2xl lg:text-[26px] font-extrabold text-[#162721] tracking-tight font-display">
              Satellite Datasets & Constellations
            </h1>

            <p className="text-xs text-[#5f7168] max-w-3xl mt-1 leading-relaxed">
              Standardized optical, multispectral, and microwave synthetic aperture radar (SAR) sensor pipelines ingested and indexed for visual-language querying.
            </p>
          </div>

          <button
            onClick={() => navigate('/new-analysis')}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#234238] hover:bg-[#1a342c] text-white rounded-lg text-xs font-semibold shadow-md shadow-[#234238]/20 transition-all self-start"
          >
            <Sparkles size={13} strokeWidth={2.4} />
            <span>Launch New Analysis</span>
          </button>
        </div>

        {/* Filter Bar */}
        <div className="bg-white rounded-xl border border-[#e5ebe7] p-2 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
          <div className="relative w-full md:max-w-md flex items-center">
            <Search size={15} className="absolute left-3.5 text-slate-400 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search datasets by satellite, sensor, band, or application..."
              className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50/60 hover:bg-slate-50 focus:bg-white border border-slate-200/80 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#234238] focus:border-[#234238] transition-colors font-body"
            />
          </div>

          <div className="flex items-center gap-1.5 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
            {modalities.map((mod) => (
              <button
                key={mod}
                onClick={() => setSelectedModality(mod)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                  selectedModality === mod
                    ? 'bg-[#234238] text-white shadow-sm'
                    : 'bg-white hover:bg-[#f2f6f4] text-slate-600 border border-[#d8e0dc]'
                }`}
              >
                {mod}
              </button>
            ))}
          </div>
        </div>

        {/* Datasets List Cards */}
        <div className="space-y-4">
          {filteredDatasets.map((ds) => (
            <div
              key={ds.id}
              className="bg-white rounded-xl border border-[#e5ebe7] p-5 shadow-sm hover:shadow transition-shadow space-y-4"
            >
              {/* Header Info */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[#e2eae5] border border-[#c8d4ce] text-[#234238] flex items-center justify-center shrink-0 mt-0.5">
                    {ds.modality.includes('SAR') ? (
                      <Radio size={20} className="text-[#234238]" />
                    ) : (
                      <Satellite size={20} className="text-[#234238]" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-display font-bold text-base text-[#162721]">{ds.name}</h3>
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600">
                        {ds.agency}
                      </span>
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-[#e2eae5] border border-[#c8d4ce] text-[#234238]">
                        {ds.modality}
                      </span>
                    </div>
                    <p className="text-xs text-[#5f7168] mt-1">
                      Platform: <span className="text-slate-700 font-medium">{ds.platform}</span> · Revisit:{' '}
                      <span className="text-slate-700 font-medium">{ds.revisit}</span> · Swath:{' '}
                      <span className="text-slate-700 font-medium">{ds.swathWidth}</span>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleQuickAnalyze(ds)}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#e2eae5] hover:bg-[#d4e1da] text-[#234238] border border-[#c8d4ce] rounded-lg text-xs font-semibold transition-colors"
                  >
                    <span>Quick Analyze</span>
                    <ArrowRight size={13} />
                  </button>
                </div>
              </div>

              {/* Grid: Resolution, Data Tier, Availability */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-200/70">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                    Spatial Resolution
                  </span>
                  <span className="font-semibold text-slate-800 text-xs mt-0.5 block">{ds.resolution}</span>
                </div>

                <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-200/70">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                    Product Level / Tier
                  </span>
                  <span className="font-semibold text-slate-800 text-xs mt-0.5 block truncate">
                    {ds.dataTier}
                  </span>
                </div>

                <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-200/70">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                    Archive Availability
                  </span>
                  <span className="font-semibold text-slate-800 text-xs mt-0.5 block truncate">
                    {ds.availability}
                  </span>
                </div>
              </div>

              {/* Spectral Bands Table */}
              <div>
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                  Spectral Configuration & Channels
                </span>
                <div className="overflow-x-auto rounded-lg border border-slate-200">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 text-[11px]">
                      <tr>
                        <th className="py-2 px-3">Band / Channel</th>
                        <th className="py-2 px-3">Description</th>
                        <th className="py-2 px-3">Center Wavelength</th>
                        <th className="py-2 px-3">Native Resolution</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {ds.bands.map((b, idx) => (
                        <tr key={idx} className="hover:bg-slate-50/60">
                          <td className="py-1.5 px-3 font-semibold text-[#234238]">{b.band}</td>
                          <td className="py-1.5 px-3">{b.name}</td>
                          <td className="py-1.5 px-3 text-slate-500">{b.center}</td>
                          <td className="py-1.5 px-3">{b.res}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Applications Tags */}
              <div className="flex items-center gap-2 flex-wrap pt-1">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  Applications:
                </span>
                {ds.applications.map((app, i) => (
                  <span
                    key={i}
                    className="text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200/60"
                  >
                    {app}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
