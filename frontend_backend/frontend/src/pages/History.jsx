import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  Sparkles,
  Download,
  CheckCircle2,
  Clock,
  Globe,
  Activity,
  RotateCcw,
  Sliders,
  Calendar,
  AlertCircle,
  ArrowRight,
  X,
  Copy,
  Check,
  Cpu,
  Layers,
  FileDown,
  Database,
  Satellite,
  Radio,
  Terminal,
} from 'lucide-react'
import { auditMetrics, executionLogRecords } from '../data/mockData'

export default function History() {
  const navigate = useNavigate()

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('All') // 'All' | 'Completed' | 'Processing' | 'Failed'

  // Selected record for Telemetry Modal
  const [selectedTelemetry, setSelectedTelemetry] = useState(null)
  const [copiedTelemetry, setCopiedTelemetry] = useState(false)

  // Notification Toast for Rerun / Export
  const [toastMessage, setToastMessage] = useState(null)
  const [rerunningId, setRerunningId] = useState(null)

  const showToast = (msg) => {
    setToastMessage(msg)
    setTimeout(() => setToastMessage(null), 3500)
  }

  // Counts for status pills
  const counts = useMemo(() => {
    return {
      all: executionLogRecords.length,
      completed: executionLogRecords.filter((r) => r.status === 'Completed').length,
      processing: executionLogRecords.filter((r) => r.status === 'Processing').length,
      failed: executionLogRecords.filter((r) => r.status === 'Failed').length,
    }
  }, [])

  // Filtered records
  const filteredRecords = useMemo(() => {
    return executionLogRecords.filter((item) => {
      // Status filter
      if (statusFilter !== 'All' && item.status !== statusFilter) {
        return false
      }
      // Search filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim()
        const matchesPrompt = item.prompt.toLowerCase().includes(q)
        const matchesRegion = item.region.toLowerCase().includes(q)
        const matchesSensor = item.sensor.toLowerCase().includes(q)
        const matchesId = item.id.toLowerCase().includes(q)
        const matchesResult = item.resultSummary.toLowerCase().includes(q)
        return matchesPrompt || matchesRegion || matchesSensor || matchesId || matchesResult
      }
      return true
    })
  }, [searchQuery, statusFilter])

  // Handle Rerun simulation
  const handleRerun = (item) => {
    setRerunningId(item.id)
    setTimeout(() => {
      setRerunningId(null)
      showToast(`Pipeline ${item.id} re-queued on NRSC High-Performance Cluster.`)
    }, 900)
  }

  // Handle Open Workspace
  const handleOpenWorkspace = (item) => {
    navigate('/new-analysis', {
      state: {
        presetQuery: item.prompt,
        region: item.region,
        sensor: item.sensor,
      },
    })
  }

  // Handle Export Audit JSON
  const handleExportJSON = () => {
    const dataToExport = {
      exportTimestamp: new Date().toISOString(),
      archiveName: 'ISRO EO TELEMETRY ARCHIVE',
      auditQuarter: '2026.Q3',
      metrics: auditMetrics,
      totalExported: filteredRecords.length,
      records: filteredRecords,
    }
    const blob = new Blob([JSON.stringify(dataToExport, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `SatQuery_Audit_Log_2026_Q3_${statusFilter.toLowerCase()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    showToast(`Audit log exported as JSON (${filteredRecords.length} records)`)
  }

  // Handle Copy Telemetry JSON
  const handleCopyTelemetry = () => {
    if (!selectedTelemetry) return
    navigator.clipboard.writeText(JSON.stringify(selectedTelemetry, null, 2))
    setCopiedTelemetry(true)
    setTimeout(() => setCopiedTelemetry(false), 2000)
  }

  return (
    <div className="flex-1 overflow-y-auto bg-[#fafaf8] px-4 py-6 md:px-8 lg:px-12 text-[#162721] selection:bg-[#dce7e1] selection:text-[#162721]">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Toast alert */}
        {toastMessage && (
          <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-slate-900 text-white text-xs font-medium px-4 py-3 rounded-xl shadow-2xl border border-slate-700 animate-fadeUp">
            <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
        )}

        {/* Header section with Breadcrumb & Actions */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            {/* Top tiny breadcrumb */}
            <div className="flex items-center gap-2 text-[11px] font-semibold tracking-wider text-[#234238] mb-1">
              <Radio size={13} className="text-[#234238] animate-pulse" />
              <span>ISRO EO TELEMETRY ARCHIVE</span>
              <span className="text-slate-300">/</span>
              <span className="text-[#5f7168] font-normal">Audit Trail 2026.Q3</span>
            </div>

            {/* Main Title */}
            <h1 className="text-2xl lg:text-[26px] font-extrabold text-[#162721] tracking-tight font-display">
              Analysis History & Audit Log
            </h1>

            {/* Subtitle */}
            <p className="text-xs text-[#5f7168] max-w-3xl mt-1 leading-relaxed">
              Chronologically indexed satellite visual-language inferences, sensor pipelines, and execution telemetry across regional observation zones.
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2.5 shrink-0 self-start">
            <button
              onClick={handleExportJSON}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-white hover:bg-[#f2f6f4] border border-[#d8e0dc] text-[#234238] rounded-lg text-xs font-semibold shadow-sm transition-all"
            >
              <Download size={13} className="text-[#234238]" />
              <span>Export Audit JSON</span>
            </button>

            <button
              onClick={() => navigate('/new-analysis')}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#234238] hover:bg-[#1a342c] text-white rounded-lg text-xs font-semibold shadow-md shadow-[#234238]/20 transition-all"
            >
              <Sparkles size={13} strokeWidth={2.4} />
              <span>New Analysis</span>
            </button>
          </div>
        </div>

        {/* 4 Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {/* Card 1: TOTAL INFERENCES */}
          <div className="bg-white rounded-xl border border-[#e5ebe7] p-4 shadow-sm hover:shadow transition-shadow">
            <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <span>TOTAL INFERENCES</span>
              <Activity size={14} className="text-[#234238]" />
            </div>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-2xl lg:text-[28px] font-bold text-[#162721] tracking-tight">
                {auditMetrics.totalInferences}
              </span>
              <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 border border-emerald-200/60 px-1.5 py-0.5 rounded-md">
                {auditMetrics.weeklyGrowth}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">{auditMetrics.subtitle1}</p>
          </div>

          {/* Card 2: PIPELINE SUCCESS RATE */}
          <div className="bg-white rounded-xl border border-[#e5ebe7] p-4 shadow-sm hover:shadow transition-shadow">
            <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <span>PIPELINE SUCCESS</span>
              <CheckCircle2 size={14} className="text-emerald-500" />
            </div>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-2xl lg:text-[28px] font-bold text-[#162721] tracking-tight">
                {auditMetrics.successRate}
              </span>
              <span className="text-xs text-slate-400 font-mono font-medium">
                {auditMetrics.failedCount} failed
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">{auditMetrics.subtitle2}</p>
          </div>

          {/* Card 3: AVG LATENCY */}
          <div className="bg-white rounded-xl border border-[#e5ebe7] p-4 shadow-sm hover:shadow transition-shadow">
            <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <span>AVG LATENCY</span>
              <Clock size={14} className="text-[#234238]" />
            </div>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-2xl lg:text-[28px] font-bold text-[#162721] tracking-tight">
                {auditMetrics.avgLatency}
              </span>
              <span className="text-xs text-slate-400 font-mono font-medium">
                {auditMetrics.p95}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">{auditMetrics.subtitle3}</p>
          </div>

          {/* Card 4: ACTIVE CONSTELLATIONS */}
          <div className="bg-white rounded-xl border border-[#e5ebe7] p-4 shadow-sm hover:shadow transition-shadow">
            <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <span>ACTIVE CONSTELLATIONS</span>
              <Globe size={14} className="text-[#234238]" />
            </div>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-2xl lg:text-[28px] font-bold text-[#162721] tracking-tight">
                {auditMetrics.activeConstellations}
              </span>
              <span className="text-xs font-medium text-slate-700">Sensors</span>
              <span className="text-[10px] font-semibold text-[#234238] bg-[#e2eae5] border border-[#c8d4ce] px-1.5 py-0.5 rounded">
                {auditMetrics.levelBadge}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1 truncate">{auditMetrics.subtitle4}</p>
          </div>
        </div>

        {/* Search and Filter Pill Bar */}
        <div className="bg-white rounded-xl border border-[#e5ebe7] p-2 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
          {/* Search Input */}
          <div className="relative w-full md:max-w-md flex items-center">
            <Search size={15} className="absolute left-3.5 text-slate-400 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search history by query, region, sensor, or ID..."
              className="w-full pl-9 pr-8 py-2 text-xs bg-slate-50/60 hover:bg-slate-50 focus:bg-white border border-slate-200/80 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#234238] focus:border-[#234238] transition-colors font-body"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2.5 text-slate-400 hover:text-slate-600 p-0.5"
              >
                <X size={13} />
              </button>
            )}
          </div>

          {/* Status Filter Buttons */}
          <div className="flex items-center gap-1.5 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
            {/* All Statuses */}
            <button
              onClick={() => setStatusFilter('All')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 whitespace-nowrap ${
                statusFilter === 'All'
                  ? 'bg-[#234238] text-white shadow-sm'
                  : 'bg-white hover:bg-[#f2f6f4] text-slate-600 border border-[#d8e0dc]'
              }`}
            >
              <span>All Statuses</span>
            </button>

            {/* Completed */}
            <button
              onClick={() => setStatusFilter('Completed')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 whitespace-nowrap ${
                statusFilter === 'Completed'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-white hover:bg-emerald-50 text-slate-600 border border-slate-200/90'
              }`}
            >
              <CheckCircle2
                size={12}
                className={statusFilter === 'Completed' ? 'text-white' : 'text-emerald-500'}
              />
              <span>Completed</span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                  statusFilter === 'Completed'
                    ? 'bg-emerald-700/60 text-white'
                    : 'bg-slate-100 text-slate-500'
                }`}
              >
                {counts.completed}
              </span>
            </button>

            {/* Processing */}
            <button
              onClick={() => setStatusFilter('Processing')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 whitespace-nowrap ${
                statusFilter === 'Processing'
                  ? 'bg-[#234238] text-white shadow-sm'
                  : 'bg-white hover:bg-[#f2f6f4] text-slate-600 border border-[#d8e0dc]'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  statusFilter === 'Processing' ? 'bg-white' : 'bg-[#234238]'
                } animate-pulse`}
              />
              <span>Processing</span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                  statusFilter === 'Processing'
                    ? 'bg-[#1a342c] text-white'
                    : 'bg-slate-100 text-slate-500'
                }`}
              >
                {counts.processing}
              </span>
            </button>

            {/* Failed */}
            <button
              onClick={() => setStatusFilter('Failed')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 whitespace-nowrap ${
                statusFilter === 'Failed'
                  ? 'bg-rose-600 text-white shadow-sm'
                  : 'bg-white hover:bg-rose-50 text-slate-600 border border-slate-200/90'
              }`}
            >
              <AlertCircle
                size={12}
                className={statusFilter === 'Failed' ? 'text-white' : 'text-rose-500'}
              />
              <span>Failed</span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                  statusFilter === 'Failed'
                    ? 'bg-rose-700/60 text-white'
                    : 'bg-slate-100 text-slate-500'
                }`}
              >
                {counts.failed}
              </span>
            </button>
          </div>
        </div>

        {/* Section Heading */}
        <div className="flex items-center justify-between pt-1">
          <div>
            <h2 className="text-sm font-bold text-slate-900 tracking-tight">
              Chronological Pipeline Execution Log
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Detailed record of natural language prompts mapped to optical/multispectral raster outputs.
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Displaying {filteredRecords.length} of {executionLogRecords.length} records
          </span>
        </div>

        {/* Execution Log Timeline */}
        <div className="relative pl-6 lg:pl-8 space-y-4">
          {/* Continuous vertical timeline connector line */}
          <div className="absolute left-[11px] lg:left-[15px] top-6 bottom-6 w-0.5 bg-slate-200/90 -translate-x-1/2" />

          {filteredRecords.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-500">
              <Search size={32} className="mx-auto text-slate-300 mb-3" />
              <p className="text-sm font-semibold text-slate-700">No matching telemetry records found</p>
              <p className="text-xs text-slate-400 mt-1">
                Try loosening your search keywords or resetting your status filter.
              </p>
              <button
                onClick={() => {
                  setSearchQuery('')
                  setStatusFilter('All')
                }}
                className="mt-4 px-3.5 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50 border border-blue-200 rounded-lg transition-colors"
              >
                Reset Filters
              </button>
            </div>
          ) : (
            filteredRecords.map((item) => {
              const isProcessing = item.status === 'Processing'
              const isFailed = item.status === 'Failed'
              const isCompleted = item.status === 'Completed'

              return (
                <div key={item.id} className="relative group">
                  {/* Timeline Status Dot */}
                  <div className="absolute -left-6 lg:-left-8 top-5 -translate-x-1/2 flex items-center justify-center z-10">
                    {isCompleted && (
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-100" />
                    )}
                    {isProcessing && (
                      <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#234238]/40 opacity-75" />
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-[#234238] ring-4 ring-[#234238]/10" />
                      </span>
                    )}
                    {isFailed && (
                      <span className="w-2.5 h-2.5 rounded-full bg-rose-500 ring-4 ring-rose-100" />
                    )}
                  </div>

                  {/* Main Card */}
                  <div className="bg-white rounded-xl border border-[#e5ebe7] p-4 md:p-5 shadow-sm hover:shadow-md transition-all">
                    {/* Top Row: Date, ID, Sensor, Status & Latency */}
                    <div className="flex flex-wrap items-center justify-between gap-2.5 pb-2.5">
                      {/* Left: Date + ID + Sensor */}
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <div className="flex items-center gap-1.5 text-slate-700 font-mono font-medium">
                          <Calendar size={13} className="text-slate-400" />
                          <span>
                            {item.date} · {item.time}
                          </span>
                        </div>

                        <span className="text-slate-300">|</span>

                        {/* ID Badge */}
                        <span className="font-mono text-[11px] text-slate-600 bg-slate-100/90 border border-slate-200/80 px-2 py-0.5 rounded tracking-tight">
                          ID: {item.id}
                        </span>

                        {/* Sensor Pill */}
                        <span className="text-[11px] font-semibold text-[#234238] bg-[#e2eae5] border border-[#c8d4ce] px-2.5 py-0.5 rounded-md">
                          {item.sensor}
                        </span>
                      </div>

                      {/* Right: Status Pill + Latency */}
                      <div className="flex items-center gap-2">
                        {isCompleted && (
                          <span className="text-[11.5px] font-medium text-emerald-700 bg-emerald-50/90 border border-emerald-200/80 px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
                            <CheckCircle2 size={12} className="text-emerald-600" />
                            <span>Completed</span>
                          </span>
                        )}
                        {isProcessing && (
                          <span className="text-[11.5px] font-medium text-[#234238] bg-[#e2eae5] border border-[#c8d4ce] px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#234238] animate-pulse" />
                            <span>Processing</span>
                          </span>
                        )}
                        {isFailed && (
                          <span className="text-[11.5px] font-medium text-rose-700 bg-rose-50/90 border border-rose-200/80 px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
                            <AlertCircle size={12} className="text-rose-600" />
                            <span>Failed</span>
                          </span>
                        )}

                        {/* Latency Box */}
                        <span className="font-mono text-[11px] text-slate-500 border border-slate-200 bg-slate-50/70 px-2 py-0.5 rounded min-w-[36px] text-center">
                          {item.latency}
                        </span>
                      </div>
                    </div>

                    {/* Middle: Natural Language Prompt */}
                    <div className="mt-1">
                      <p className="text-[15px] font-bold text-[#162721] tracking-tight">
                        &ldquo;{item.prompt}&rdquo;
                      </p>
                      <p className="text-xs text-[#5f7168] mt-1 font-normal">
                        {item.resultSummary}
                      </p>
                    </div>

                    {/* Bottom Row: Target Region, Model Confidence & Action Buttons */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-4 pt-3 border-t border-slate-100">
                      {/* Left: Region & Confidence */}
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <span>Target Region:</span>
                        <span className="font-semibold text-slate-800">{item.region}</span>
                        <span className="text-slate-300">·</span>
                        <span>Model Confidence:</span>
                        <span
                          className={`font-mono font-bold ${
                            item.confidence === 'N/A' ? 'text-slate-400' : 'text-[#234238]'
                          }`}
                        >
                          {item.confidence}
                        </span>
                      </div>

                      {/* Right: Actions */}
                      <div className="flex items-center gap-2 shrink-0">
                        <button
                          onClick={() => handleOpenWorkspace(item)}
                          className="text-xs font-semibold text-[#234238] hover:text-[#1a342c] flex items-center gap-1 px-2.5 py-1.5 rounded-lg hover:bg-[#f2f6f4] transition-colors"
                        >
                          <span>Open Workspace</span>
                          <ArrowRight size={13} />
                        </button>

                        <button
                          onClick={() => handleRerun(item)}
                          disabled={rerunningId === item.id}
                          className="text-xs font-medium text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-200 px-2.5 py-1.5 rounded-lg flex items-center gap-1.5 shadow-sm transition-all"
                        >
                          <RotateCcw
                            size={12}
                            className={`text-slate-500 ${rerunningId === item.id ? 'animate-spin' : ''}`}
                          />
                          <span>Rerun</span>
                        </button>

                        <button
                          onClick={() => setSelectedTelemetry(item)}
                          className="text-xs font-medium text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-200 px-2.5 py-1.5 rounded-lg flex items-center gap-1.5 shadow-sm transition-all"
                        >
                          <Sliders size={12} className="text-slate-500" />
                          <span>Telemetry</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Telemetry Inspector Modal / Drawer */}
      {selectedTelemetry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeUp">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/80">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#e2eae5] text-[#234238] flex items-center justify-center">
                  <Sliders size={16} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-slate-900 text-sm">
                      Pipeline Telemetry Inspector
                    </h3>
                    <span className="font-mono text-xs text-[#234238] bg-[#e2eae5] border border-[#c8d4ce] px-2 py-0.5 rounded">
                      {selectedTelemetry.id}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Execution Profile & Multispectral Ingestion Metrics
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedTelemetry(null)}
                className="text-slate-400 hover:text-slate-700 p-1.5 rounded-lg hover:bg-slate-200/60 transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-5 text-xs">
              {/* Natural Language Prompt Banner */}
              <div className="bg-[#f4f7f5] border border-[#d8e0dc] rounded-xl p-3.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#234238] block mb-1">
                  Query Prompt
                </span>
                <p className="text-sm font-semibold text-slate-800">
                  &ldquo;{selectedTelemetry.prompt}&rdquo;
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Output: {selectedTelemetry.resultSummary}
                </p>
              </div>

              {/* Grid of Key Properties */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase block">Sensor</span>
                  <span className="font-semibold text-slate-800 text-xs mt-0.5 block truncate">
                    {selectedTelemetry.sensor}
                  </span>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase block">Latency</span>
                  <span className="font-semibold text-slate-800 font-mono text-xs mt-0.5 block">
                    {selectedTelemetry.latency}
                  </span>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase block">Confidence</span>
                  <span className="font-semibold text-[#234238] font-mono text-xs mt-0.5 block">
                    {selectedTelemetry.confidence}
                  </span>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase block">Cloud Cover</span>
                  <span className="font-semibold text-slate-800 text-xs mt-0.5 block">
                    {selectedTelemetry.telemetry?.cloudCover || 'N/A'}
                  </span>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase block">Resolution (GSD)</span>
                  <span className="font-semibold text-slate-800 text-xs mt-0.5 block truncate">
                    {selectedTelemetry.telemetry?.gsd || 'N/A'}
                  </span>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase block">Tokens Processed</span>
                  <span className="font-semibold text-slate-800 font-mono text-xs mt-0.5 block">
                    {selectedTelemetry.telemetry?.tokensUsed || 0}
                  </span>
                </div>
              </div>

              {/* Execution Latency Waterfall Breakdown */}
              {selectedTelemetry.telemetry?.latencyBreakdown && (
                <div>
                  <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Clock size={12} className="text-slate-500" />
                    Pipeline Latency Waterfall
                  </h4>
                  <div className="space-y-1.5 bg-slate-50 p-3 rounded-xl border border-slate-200">
                    {Object.entries(selectedTelemetry.telemetry.latencyBreakdown).map(
                      ([stage, duration]) => (
                        <div key={stage} className="flex items-center justify-between text-xs">
                          <span className="text-slate-600 capitalize">
                            {stage.replace(/([A-Z])/g, ' $1')}
                          </span>
                          <span className="font-mono font-semibold text-slate-800">
                            {duration}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}

              {/* Hardware & Cluster Details */}
              <div className="space-y-2">
                <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <Cpu size={12} className="text-slate-500" />
                  Compute Infrastructure
                </h4>
                <div className="p-3 bg-slate-900 text-slate-200 rounded-xl font-mono text-[11px] space-y-1">
                  <div>
                    <span className="text-slate-400">Model Engine: </span>
                    <span className="text-emerald-400">
                      {selectedTelemetry.telemetry?.inferenceEngine || 'SatQuery-VLM'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Cluster Node: </span>
                    <span className="text-sky-300">
                      {selectedTelemetry.telemetry?.gpuCluster || 'ISRO-H100-NODE'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Scene Identifier: </span>
                    <span className="text-slate-300">
                      {selectedTelemetry.telemetry?.sceneId || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Band Configuration: </span>
                    <span className="text-amber-300">
                      {selectedTelemetry.telemetry?.bands || 'Multispectral'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Failure Error Reason if any */}
              {selectedTelemetry.telemetry?.errorReason && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
                  <span className="font-bold block mb-0.5">Failure Reason:</span>
                  <p>{selectedTelemetry.telemetry.errorReason}</p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
              <button
                onClick={handleCopyTelemetry}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
              >
                {copiedTelemetry ? (
                  <>
                    <Check size={13} className="text-emerald-600" />
                    <span className="text-emerald-600">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy size={13} />
                    <span>Copy JSON</span>
                  </>
                )}
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedTelemetry(null)}
                  className="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    const item = selectedTelemetry
                    setSelectedTelemetry(null)
                    handleOpenWorkspace(item)
                  }}
                  className="px-3.5 py-1.5 bg-[#234238] hover:bg-[#1a342c] text-white rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors"
                >
                  <span>Open in Workspace</span>
                  <ArrowRight size={13} />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
