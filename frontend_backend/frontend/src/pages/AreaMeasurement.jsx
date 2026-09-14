import { useState, useRef } from 'react'
import {
  Ruler,
  Upload,
  RefreshCw,
  Download,
  Crosshair,
  Search,
  Layers,
  BarChart2,
  X,
} from 'lucide-react'
import DownloadReportButton from '../components/DownloadReportButton'

const BACKEND_URL = 'http://localhost:8000'

export default function AreaMeasurement() {
  const [activeTab, setActiveTab] = useState('area') // 'area' | 'grounding'

  // Area state
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [satelliteMode, setSatelliteMode] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [areaResult, setAreaResult] = useState(null)
  const [error, setError] = useState(null)

  // Grounding state
  const [groundFile, setGroundFile] = useState(null)
  const [groundPreview, setGroundPreview] = useState(null)
  const [query, setQuery] = useState('')
  const [boxThreshold, setBoxThreshold] = useState(0.2)
  const [grounding, setGrounding] = useState(false)
  const [groundResult, setGroundResult] = useState(null)
  const [groundError, setGroundError] = useState(null)

  const fileInputRef = useRef(null)
  const groundFileInputRef = useRef(null)

  // Drag handlers
  const handleDragOver = (e) => { e.preventDefault(); e.stopPropagation() }
  const handleDrop = (e, setter, previewSetter) => {
    e.preventDefault(); e.stopPropagation()
    const f = e.dataTransfer.files[0]
    if (f) { setter(f); previewSetter(URL.createObjectURL(f)) }
  }

  const handleFileSelect = (e, setter, previewSetter) => {
    const f = e.target.files?.[0]
    if (f) { setter(f); previewSetter(URL.createObjectURL(f)) }
  }

  // Area analysis
  const handleAnalyze = async () => {
    if (!file) return
    setAnalyzing(true)
    setError(null)
    setAreaResult(null)

    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('satellite_mode', satelliteMode ? 'true' : 'false')

      const res = await fetch(`${BACKEND_URL}/api/v1/area/analyze`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok || !data.success) throw new Error(data.detail || data.error || 'Analysis failed')
      setAreaResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setAnalyzing(false)
    }
  }

  // Object grounding
  const handleGround = async () => {
    if (!groundFile || !query.trim()) return
    setGrounding(true)
    setGroundError(null)
    setGroundResult(null)

    try {
      const formData = new FormData()
      formData.append('image', groundFile)
      formData.append('query', query)
      formData.append('box_threshold', boxThreshold)

      const res = await fetch(`${BACKEND_URL}/api/v1/area/ground`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok || !data.success) throw new Error(data.detail || data.error || 'Grounding failed')
      setGroundResult(data)
    } catch (err) {
      setGroundError(err.message)
    } finally {
      setGrounding(false)
    }
  }

  return (
    <div className="flex-1 overflow-y-auto bg-[#fafaf8]">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-[#162721] flex items-center gap-2">
              <Ruler size={22} className="text-[#2d5243]" />
              Area Measurement & Object Grounding
            </h1>
            <p className="text-sm text-[#6b7c73] mt-0.5">
              Land-cover segmentation, area calculation & open-vocabulary object detection
            </p>
          </div>
          <div className="text-xs text-[#7a9486] bg-[#edf2ef] border border-[#dce7e1] rounded-lg px-3 py-1.5 font-mono">
            Ref: BigEarthNet.txt (arXiv:2603.29630)
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-[#f4f7f5] p-0.5 rounded-lg border border-[#dce7e1] w-fit">
          <button
            onClick={() => setActiveTab('area')}
            className={`px-4 py-1.5 text-xs font-semibold rounded-md transition flex items-center gap-1.5 ${
              activeTab === 'area'
                ? 'bg-[#234238] text-white shadow-sm'
                : 'text-[#5c7569] hover:text-[#162721]'
            }`}
          >
            <Layers size={13} /> Area Measurement
          </button>
          <button
            onClick={() => setActiveTab('grounding')}
            className={`px-4 py-1.5 text-xs font-semibold rounded-md transition flex items-center gap-1.5 ${
              activeTab === 'grounding'
                ? 'bg-[#234238] text-white shadow-sm'
                : 'text-[#5c7569] hover:text-[#162721]'
            }`}
          >
            <Crosshair size={13} /> Object Grounding
          </button>
        </div>

        {/* ── AREA MEASUREMENT TAB ── */}
        {activeTab === 'area' && (
          <div className="space-y-6">
            {/* Upload Card */}
            <div className="bg-white border border-[#e5ebe7] rounded-xl p-5 shadow-2xs">
              <h2 className="text-sm font-bold text-[#162721] mb-3">Upload Satellite Imagery</h2>
              <p className="text-xs text-[#6b7c73] mb-4">
                Select an image to analyze land-cover area (Supports RGB, GeoTIFF, Sentinel data)
              </p>

              <div
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, setFile, setPreview)}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-[#c8d5cc] hover:border-[#2d5243] rounded-xl p-8 text-center cursor-pointer transition bg-[#f9fbfa] hover:bg-[#f0f5f2]"
              >
                <input ref={fileInputRef} type="file" className="hidden" accept=".jpg,.jpeg,.png,.tif,.tiff,.bmp,.webp" onChange={(e) => handleFileSelect(e, setFile, setPreview)} />
                {preview ? (
                  <div className="flex flex-col items-center gap-2">
                    <img src={preview} alt="Preview" className="max-h-28 rounded-lg border border-[#dce7e1]" />
                    <span className="text-xs text-[#5c7569]">{file?.name}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2 text-[#7a9486]">
                    <Upload size={32} />
                    <span className="text-xs font-medium">Drag & drop image here or click to browse</span>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between mt-4 gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <div className={`w-9 h-5 rounded-full transition-colors relative ${satelliteMode ? 'bg-[#2d5243]' : 'bg-[#c8d5cc]'}`}>
                    <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform shadow-sm ${satelliteMode ? 'left-[18px]' : 'left-0.5'}`} />
                  </div>
                  <input type="checkbox" className="hidden" checked={satelliteMode} onChange={(e) => setSatelliteMode(e.target.checked)} />
                  <span className="text-xs text-[#5c7569] font-medium">Satellite Mode (HSV analysis)</span>
                </label>

                <button
                  onClick={handleAnalyze}
                  disabled={!file || analyzing}
                  className="px-5 py-2 bg-[#234238] hover:bg-[#1b342c] text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition shadow-sm disabled:opacity-40 cursor-pointer"
                >
                  {analyzing ? <RefreshCw size={14} className="animate-spin" /> : <BarChart2 size={14} />}
                  <span>{analyzing ? 'Analyzing...' : 'Analyze Area'}</span>
                </button>
              </div>

              {error && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">{error}</div>
              )}
            </div>

            {/* Results */}
            {areaResult && (
              <div className="space-y-5">
                {/* Stats Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="bg-white border border-[#e5ebe7] rounded-xl p-3.5 shadow-2xs">
                    <div className="text-[11px] text-[#7a9486] font-medium">Total Coverage</div>
                    <div className="text-lg font-bold text-[#162721] mt-0.5">{areaResult.total_coverage_percent}%</div>
                  </div>
                  <div className="bg-white border border-[#e5ebe7] rounded-xl p-3.5 shadow-2xs">
                    <div className="text-[11px] text-[#7a9486] font-medium">Detected Classes</div>
                    <div className="text-lg font-bold text-[#162721] mt-0.5">{areaResult.classes.length}</div>
                  </div>
                  <div className="bg-white border border-[#e5ebe7] rounded-xl p-3.5 shadow-2xs">
                    <div className="text-[11px] text-[#7a9486] font-medium">Processing Time</div>
                    <div className="text-lg font-bold text-[#162721] mt-0.5">{areaResult.processing_time_seconds}s</div>
                  </div>
                  <div className="bg-white border border-[#e5ebe7] rounded-xl p-3.5 shadow-2xs">
                    <div className="text-[11px] text-[#7a9486] font-medium">Resolution</div>
                    <div className="text-lg font-bold text-[#162721] mt-0.5">
                      {areaResult.spatial_resolution_m ? `${areaResult.spatial_resolution_m.toFixed(1)} m/px` : 'N/A'}
                    </div>
                  </div>
                </div>

                {/* Image Comparison */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white border border-[#e5ebe7] rounded-xl overflow-hidden shadow-2xs">
                    <div className="px-4 py-2.5 border-b border-[#e5ebe7] text-xs font-bold text-[#162721]">Original Image</div>
                    <div className="p-3">
                      <img src={`data:image/png;base64,${areaResult.original_image}`} alt="Original" className="w-full rounded-lg" />
                    </div>
                  </div>
                  <div className="bg-white border border-[#e5ebe7] rounded-xl overflow-hidden shadow-2xs">
                    <div className="px-4 py-2.5 border-b border-[#e5ebe7] flex items-center justify-between">
                      <span className="text-xs font-bold text-[#162721]">Area Annotation</span>
                      <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#edf2ef] text-[#2d5243] border border-[#dce7e1] rounded-full">
                        {areaResult.model_used?.split(' ')[0]}
                      </span>
                    </div>
                    <div className="p-3">
                      <img src={`data:image/png;base64,${areaResult.annotated_image}`} alt="Annotated" className="w-full rounded-lg" />
                    </div>
                  </div>
                </div>

                {/* Data Table */}
                <div className="bg-white border border-[#e5ebe7] rounded-xl overflow-hidden shadow-2xs">
                  <div className="px-4 py-3 border-b border-[#e5ebe7] flex items-center justify-between flex-wrap gap-2">
                    <h3 className="text-sm font-bold text-[#162721]">Land Cover Summary</h3>
                    <div className="flex items-center gap-2">
                      <DownloadReportButton
                        reportData={{
                          title: 'Land Cover Area Measurement & Segmentation Report',
                          analysisType: 'Area Measurement & Segmentation',
                          modelUsed: areaResult.model_used || 'DeepLabV3+ ResNet-50 / LULC',
                          prediction: `Land cover segmentation identified ${areaResult.classes.length} surface classes covering ${areaResult.total_coverage_percent}% of the scene.`,
                          sceneDetails: {
                            'Source File': file ? file.name : (selectedSample ? selectedSample.title : 'Satellite Scene'),
                            'Spatial Resolution': areaResult.spatial_resolution_m ? `${areaResult.spatial_resolution_m.toFixed(1)} m/px` : 'Standard GSD',
                            'Processing Runtime': `${areaResult.processing_time_seconds}s`,
                          },
                          statistics: [
                            { label: 'Total Coverage', value: `${areaResult.total_coverage_percent}%` },
                            { label: 'Classes Detected', value: areaResult.classes.length },
                            { label: 'Processing Time', value: `${areaResult.processing_time_seconds}s` },
                            { label: 'Resolution', value: areaResult.spatial_resolution_m ? `${areaResult.spatial_resolution_m.toFixed(1)} m/px` : 'N/A' },
                          ],
                          categories: areaResult.classes.map((c) => ({
                            name: c.class_name,
                            percent: c.area_percentage,
                            areaHa: c.area_hectares,
                            extra: c.area_km2 ? `${c.area_km2} km²` : `${c.area_m2?.toLocaleString()} m²`,
                          })),
                          evidenceImages: [
                            ...(areaResult.annotated_image ? [{ title: 'Segmentation Annotation Map', src: `data:image/png;base64,${areaResult.annotated_image}` }] : []),
                            ...(areaResult.original_image ? [{ title: 'Original Satellite Scene', src: `data:image/png;base64,${areaResult.original_image}` }] : []),
                          ],
                          executionNotes: areaResult.physical_area_note,
                        }}
                      />
                      <a
                        href={`${BACKEND_URL}/api/v1/area/download`}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-[#edf2ef] hover:bg-[#dce7e1] text-[#234238] rounded-lg text-xs font-semibold transition border border-[#c8d4ce]"
                        title="Download Raw GeoTIFF/PNG"
                      >
                        <Download size={12} /> GeoTIFF
                      </a>
                    </div>
                  </div>
                  {areaResult.physical_area_note && (
                    <div className="px-4 py-1.5 bg-[#fdf8f0] border-b border-[#ece4d6] text-[11px] text-[#a08048]">
                      * {areaResult.physical_area_note}
                    </div>
                  )}
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead className="bg-[#f8faf9] border-b border-[#e5ebe7]">
                        <tr>
                          <th className="text-left px-4 py-2.5 font-semibold text-[#5c7569]">Class</th>
                          <th className="text-right px-4 py-2.5 font-semibold text-[#5c7569]">Pixel Area</th>
                          <th className="text-left px-4 py-2.5 font-semibold text-[#5c7569]">Coverage</th>
                          {areaResult.has_physical_area && (
                            <th className="text-right px-4 py-2.5 font-semibold text-[#5c7569]">Physical Area</th>
                          )}
                          <th className="text-center px-4 py-2.5 font-semibold text-[#5c7569]">Tier</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#f0f3f1]">
                        {areaResult.classes.map((cls) => (
                          <tr key={cls.class_id} className="hover:bg-[#f9fbfa] transition">
                            <td className="px-4 py-2.5">
                              <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: `rgb(${cls.color_rgb[0]},${cls.color_rgb[1]},${cls.color_rgb[2]})` }} />
                                <span className="font-medium text-[#162721]">{cls.class_name}</span>
                              </div>
                            </td>
                            <td className="px-4 py-2.5 text-right font-mono text-[#5c7569]">{cls.pixel_area.toLocaleString()}</td>
                            <td className="px-4 py-2.5">
                              <div className="flex items-center gap-2">
                                <div className="flex-1 h-1.5 bg-[#edf2ef] rounded-full overflow-hidden max-w-[100px]">
                                  <div
                                    className="h-full rounded-full"
                                    style={{ width: `${Math.min(100, cls.coverage_percent)}%`, backgroundColor: `rgb(${cls.color_rgb[0]},${cls.color_rgb[1]},${cls.color_rgb[2]})` }}
                                  />
                                </div>
                                <span className="text-[#5c7569] font-mono">{cls.coverage_percent.toFixed(2)}%</span>
                              </div>
                            </td>
                            {areaResult.has_physical_area && (
                              <td className="px-4 py-2.5 text-right text-[#5c7569]">
                                {cls.area_hectares != null ? `${cls.area_hectares.toFixed(2)} ha` : '—'}
                              </td>
                            )}
                            <td className="px-4 py-2.5 text-center">
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                                cls.coverage_tier === 'primary' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                                cls.coverage_tier === 'secondary' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                                'bg-gray-50 text-gray-500 border border-gray-200'
                              }`}>
                                {cls.coverage_tier}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── OBJECT GROUNDING TAB ── */}
        {activeTab === 'grounding' && (
          <div className="space-y-6">
            {/* Upload + Query Card */}
            <div className="bg-white border border-[#e5ebe7] rounded-xl p-5 shadow-2xs">
              <h2 className="text-sm font-bold text-[#162721] mb-1">Upload & Detect Objects</h2>
              <p className="text-xs text-[#6b7c73] mb-4">
                Upload a satellite image and describe what you want to find using natural language.
              </p>

              <div
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, setGroundFile, setGroundPreview)}
                onClick={() => groundFileInputRef.current?.click()}
                className="border-2 border-dashed border-[#c8d5cc] hover:border-[#2d5243] rounded-xl p-6 text-center cursor-pointer transition bg-[#f9fbfa] hover:bg-[#f0f5f2]"
              >
                <input ref={groundFileInputRef} type="file" className="hidden" accept=".jpg,.jpeg,.png,.tif,.tiff,.bmp,.webp" onChange={(e) => handleFileSelect(e, setGroundFile, setGroundPreview)} />
                {groundPreview ? (
                  <div className="flex flex-col items-center gap-2">
                    <img src={groundPreview} alt="Preview" className="max-h-24 rounded-lg border border-[#dce7e1]" />
                    <span className="text-xs text-[#5c7569]">{groundFile?.name}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2 text-[#7a9486]">
                    <Search size={28} />
                    <span className="text-xs font-medium">Drop image here or click to browse</span>
                  </div>
                )}
              </div>

              <div className="mt-4 space-y-3">
                <div>
                  <label className="text-xs font-semibold text-[#162721] block mb-1">What do you want to find?</label>
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., 'Where are the buildings?' or 'bridge, water, road'"
                    className="w-full px-3 py-2 border border-[#dce7e1] rounded-lg text-xs bg-[#f9fbfa] focus:outline-none focus:ring-1 focus:ring-[#2d5243]"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-[#162721] block mb-1">
                    Confidence Threshold: <span className="font-mono text-[#2d5243]">{boxThreshold.toFixed(2)}</span>
                  </label>
                  <input
                    type="range"
                    min={0.05} max={0.8} step={0.05}
                    value={boxThreshold}
                    onChange={(e) => setBoxThreshold(parseFloat(e.target.value))}
                    className="w-full accent-[#2d5243]"
                  />
                </div>
              </div>

              <button
                onClick={handleGround}
                disabled={!groundFile || !query.trim() || grounding}
                className="mt-4 px-5 py-2 bg-[#234238] hover:bg-[#1b342c] text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition shadow-sm disabled:opacity-40 cursor-pointer"
              >
                {grounding ? <RefreshCw size={14} className="animate-spin" /> : <Crosshair size={14} />}
                <span>{grounding ? 'Detecting...' : 'Detect / Ground'}</span>
              </button>

              {groundError && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">{groundError}</div>
              )}
            </div>

            {/* Grounding Results */}
            {groundResult && (
              <div className="space-y-5">
                {/* Stats */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="bg-white border border-[#e5ebe7] rounded-xl p-3.5 shadow-2xs col-span-2">
                    <div className="text-[11px] text-[#7a9486] font-medium">Visual Target</div>
                    <div className="text-base font-bold text-[#162721] mt-0.5 capitalize">{groundResult.target_label}</div>
                  </div>
                  <div className="bg-white border border-[#e5ebe7] rounded-xl p-3.5 shadow-2xs">
                    <div className="text-[11px] text-[#7a9486] font-medium">Objects Detected</div>
                    <div className="text-lg font-bold text-[#162721] mt-0.5">{groundResult.count}</div>
                  </div>
                  <div className="bg-white border border-[#e5ebe7] rounded-xl p-3.5 shadow-2xs">
                    <div className="text-[11px] text-[#7a9486] font-medium">Processing Time</div>
                    <div className="text-lg font-bold text-[#162721] mt-0.5">{groundResult.processing_time?.toFixed(1)}s</div>
                  </div>
                </div>

                {/* Images */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white border border-[#e5ebe7] rounded-xl overflow-hidden shadow-2xs">
                    <div className="px-4 py-2.5 border-b border-[#e5ebe7] text-xs font-bold text-[#162721]">Original Image</div>
                    <div className="p-3">
                      <img src={`data:image/png;base64,${groundResult.original_image}`} alt="Original" className="w-full rounded-lg" />
                    </div>
                  </div>
                  <div className="bg-white border border-[#e5ebe7] rounded-xl overflow-hidden shadow-2xs">
                    <div className="px-4 py-2.5 border-b border-[#e5ebe7] flex items-center justify-between">
                      <span className="text-xs font-bold text-[#162721]">Grounded Image</span>
                      <span className="px-2 py-0.5 text-[10px] font-semibold bg-[#edf2ef] text-[#2d5243] border border-[#dce7e1] rounded-full">
                        Grounding DINO
                      </span>
                    </div>
                    <div className="p-3">
                      <img src={`data:image/png;base64,${groundResult.annotated_image}`} alt="Detections" className="w-full rounded-lg" />
                    </div>
                  </div>
                </div>

                {/* Detection Table */}
                <div className="bg-white border border-[#e5ebe7] rounded-xl overflow-hidden shadow-2xs">
                  <div className="px-4 py-3 border-b border-[#e5ebe7] flex items-center justify-between flex-wrap gap-2">
                    <h3 className="text-sm font-bold text-[#162721]">Detection Details</h3>
                    <DownloadReportButton
                      reportData={{
                        title: 'Visual Object Grounding & Localization Report',
                        analysisType: 'Object Grounding & Localization',
                        query: query,
                        modelUsed: 'Grounding DINO Swin-T',
                        prediction: `Detected ${groundResult.count} instance(s) matching query "${query}".`,
                        confidence: groundResult.detections.length > 0
                          ? (groundResult.detections.reduce((acc, d) => acc + d.score, 0) / groundResult.detections.length)
                          : null,
                        sceneDetails: {
                          'Source File': groundFile ? groundFile.name : 'Target Scene',
                          'Query Expression': query,
                          'Processing Runtime': `${groundResult.processing_time?.toFixed(1)}s`,
                        },
                        statistics: [
                          { label: 'Objects Grounded', value: groundResult.count },
                          { label: 'Processing Time', value: `${groundResult.processing_time?.toFixed(1)}s` },
                          ...(groundResult.detections.length > 0
                            ? [{ label: 'Avg Confidence', value: `${((groundResult.detections.reduce((acc, d) => acc + d.score, 0) / groundResult.detections.length) * 100).toFixed(1)}%` }]
                            : []),
                        ],
                        categories: groundResult.detections.map((d, i) => ({
                          name: `#${i + 1} ${d.label}`,
                          percent: `${(d.score * 100).toFixed(1)}% conf`,
                          extra: `BBox [${d.box.xmin}, ${d.box.ymin}, ${d.box.xmax}, ${d.box.ymax}]`,
                        })),
                        evidenceImages: [
                          ...(groundResult.annotated_image ? [{ title: 'Grounding DINO Visual Bounding Boxes', src: `data:image/png;base64,${groundResult.annotated_image}` }] : []),
                          ...(groundResult.original_image ? [{ title: 'Original Satellite Scene', src: `data:image/png;base64,${groundResult.original_image}` }] : []),
                        ],
                      }}
                    />
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead className="bg-[#f8faf9] border-b border-[#e5ebe7]">
                        <tr>
                          <th className="text-left px-4 py-2.5 font-semibold text-[#5c7569]">#</th>
                          <th className="text-left px-4 py-2.5 font-semibold text-[#5c7569]">Label</th>
                          <th className="text-left px-4 py-2.5 font-semibold text-[#5c7569]">Color</th>
                          <th className="text-right px-4 py-2.5 font-semibold text-[#5c7569]">Confidence</th>
                          <th className="text-left px-4 py-2.5 font-semibold text-[#5c7569]">Bounding Box</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#f0f3f1]">
                        {groundResult.detections.length === 0 ? (
                          <tr>
                            <td colSpan={5} className="px-4 py-6 text-center text-[#a08048]">
                              No objects detected above threshold. Try lowering the threshold or using target terms (e.g., building, water, road).
                            </td>
                          </tr>
                        ) : (
                          groundResult.detections.map((det, idx) => (
                            <tr key={idx} className="hover:bg-[#f9fbfa] transition">
                              <td className="px-4 py-2.5 font-semibold text-[#162721]">{idx + 1}</td>
                              <td className="px-4 py-2.5 font-medium text-[#162721] uppercase">{det.label}</td>
                              <td className="px-4 py-2.5">
                                <div className="flex items-center gap-2">
                                  <div className="w-4 h-4 rounded" style={{ backgroundColor: det.color || '#ccc' }} />
                                  <span className="font-mono text-[#7a9486]">{det.color}</span>
                                </div>
                              </td>
                              <td className="px-4 py-2.5 text-right font-mono text-[#2d5243] font-semibold">
                                {(det.score * 100).toFixed(1)}%
                              </td>
                              <td className="px-4 py-2.5 font-mono text-[#5c7569]">
                                ({det.box.xmin}, {det.box.ymin}, {det.box.xmax}, {det.box.ymax})
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
