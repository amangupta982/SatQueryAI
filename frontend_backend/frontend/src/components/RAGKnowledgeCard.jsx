import { useState } from 'react'
import {
  BookOpen,
  Search,
  Sparkles,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Database,
  FileText,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Info,
} from 'lucide-react'

const SUGGESTED_QUERIES = [
  'What is SAR?',
  'What is the difference between Sentinel-1 and Sentinel-2?',
  'Why is SAR useful during cloudy conditions?',
  'What is NDVI?',
  'What is BigEarthNet.txt?',
  'What is VRSBench?',
  'Why do we combine optical and SAR imagery?',
  'Explain change detection in remote sensing.',
]

export default function RAGKnowledgeCard() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showEvidence, setShowEvidence] = useState(true)
  const [ingesting, setIngesting] = useState(false)
  const [ingestStatus, setIngestStatus] = useState(null)

  const handleSearch = async (queryToSearch) => {
    const q = queryToSearch || query
    if (!q || !q.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q.trim(),
          top_k: 5,
          score_threshold: 0.25,
        }),
      })

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('[RAG] Query error:', err)
      setError(
        'Knowledge retrieval is currently unavailable or encountered a network issue. Please check backend connection.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleIngest = async () => {
    setIngesting(true)
    setIngestStatus(null)
    try {
      const res = await fetch('/api/rag/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force_reindex: false }),
      })
      const data = await res.json()
      setIngestStatus({
        type: res.ok && data.status === 'success' ? 'success' : 'info',
        message: data.message || `Indexed ${data.documents_indexed} documents (${data.total_chunks} chunks).`,
      })
      setTimeout(() => setIngestStatus(null), 5000)
    } catch (err) {
      setIngestStatus({
        type: 'error',
        message: 'Ingestion failed. Ensure backend service is running.',
      })
      setTimeout(() => setIngestStatus(null), 5000)
    } finally {
      setIngesting(false)
    }
  }

  const handleSelectSuggested = (sq) => {
    setQuery(sq)
    handleSearch(sq)
  }

  return (
    <div
      id="rag-knowledge"
      className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden transition-all text-[#162721]"
    >
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#162721] via-[#1b322a] to-[#234238] p-5 md:p-6 text-white">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="p-2.5 rounded-xl bg-white/10 border border-white/15 text-emerald-300 shadow-inner">
              <BookOpen size={22} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-display font-bold text-lg md:text-xl tracking-tight text-white">
                  RAG / Remote Sensing Knowledge
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                  Domain RAG
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed max-w-2xl">
                Ask domain-knowledge questions about satellite constellations, SAR physics, spectral indices,
                and remote-sensing benchmarks grounded in our curated knowledge base.
              </p>
            </div>
          </div>

          {/* Re-index Utility Button */}
          <div className="flex items-center gap-2 self-start sm:self-center">
            <button
              onClick={handleIngest}
              disabled={ingesting}
              title="Re-index Knowledge Documents into Qdrant"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 text-xs font-medium text-slate-200 transition-colors cursor-pointer disabled:opacity-50"
            >
              <RefreshCw size={13} className={ingesting ? 'animate-spin text-emerald-400' : ''} />
              <span>{ingesting ? 'Ingesting...' : 'Sync KB'}</span>
            </button>
          </div>
        </div>

        {/* Ingest Status Toast */}
        {ingestStatus && (
          <div
            className={`mt-3 px-3 py-2 rounded-lg text-xs flex items-center gap-2 ${
              ingestStatus.type === 'success'
                ? 'bg-emerald-950/80 text-emerald-200 border border-emerald-600/40'
                : ingestStatus.type === 'error'
                ? 'bg-rose-950/80 text-rose-200 border border-rose-600/40'
                : 'bg-slate-800 text-slate-200 border border-slate-600'
            }`}
          >
            <Info size={14} className="shrink-0" />
            <span>{ingestStatus.message}</span>
          </div>
        )}
      </div>

      {/* Main Body */}
      <div className="p-5 md:p-6 space-y-5">
        {/* Notice of Separation */}
        <div className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
          <Info size={16} className="text-[#234238] shrink-0 mt-0.5" />
          <p className="leading-normal">
            <strong className="text-slate-800">Domain Science vs Image Vision:</strong> This RAG assistant is
            strictly for remote-sensing domain theory and documentation (e.g.{' '}
            <span className="italic">"What is SAR?"</span>, <span className="italic">"What is NDVI?"</span>).
            For direct satellite scene queries, use the visual models in the VQA, Area, or Change tabs.
          </p>
        </div>

        {/* Search Input Bar */}
        <div className="space-y-2">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500">
            Ask a question about remote sensing...
          </label>
          <div className="flex flex-col sm:flex-row items-stretch gap-2.5">
            <div className="relative flex-1">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSearch()
                }}
                placeholder="e.g. What is SAR? What is the difference between Sentinel-1 and Sentinel-2?"
                className="w-full pl-4 pr-10 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#234238]/30 focus:border-[#234238] text-sm text-slate-900 bg-white shadow-inner transition-all placeholder:text-slate-400"
              />
              <Search
                size={18}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"
              />
            </div>

            <button
              onClick={() => handleSearch()}
              disabled={loading || !query.trim()}
              className="px-6 py-3 bg-[#234238] hover:bg-[#1a342c] disabled:opacity-50 text-white text-xs font-semibold rounded-xl shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer shrink-0"
            >
              {loading ? (
                <>
                  <span className="w-3.5 h-3.5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  <span>Searching KB...</span>
                </>
              ) : (
                <>
                  <Sparkles size={14} className="text-emerald-300" />
                  <span>Ask Knowledge Base</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Suggested Question Pills */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
            Suggested Remote Sensing Inquiries:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTED_QUERIES.map((sq, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectSuggested(sq)}
                className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-[#e2eae5] hover:text-[#234238] border border-slate-200 text-xs text-slate-700 transition-colors cursor-pointer text-left"
              >
                {sq}
              </button>
            ))}
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-3">
            <AlertCircle size={16} className="text-rose-600 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="space-y-4 pt-2 border-t border-slate-200/80 animate-fadeUp">
            {/* Answer Section */}
            <div className="bg-[#fbfcfa] rounded-xl border border-slate-200 p-5 space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-600" />
                  <h4 className="font-display font-bold text-sm text-slate-900 uppercase tracking-wide">
                    Answer
                  </h4>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold">
                  Grounded in Project KB
                </span>
              </div>

              <div className="text-xs sm:text-sm text-slate-800 leading-relaxed font-body whitespace-pre-line border-t border-slate-100 pt-3">
                {result.answer}
              </div>
            </div>

            {/* Sources Section */}
            {result.sources && result.sources.length > 0 && (
              <div className="space-y-2">
                <h5 className="font-display font-bold text-xs uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                  <Database size={13} className="text-[#234238]" />
                  <span>Sources</span>
                </h5>
                <div className="flex flex-wrap gap-2">
                  {result.sources.map((src, idx) => (
                    <div
                      key={idx}
                      className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 shadow-2xs flex items-center gap-2 text-xs"
                    >
                      <FileText size={13} className="text-emerald-700 shrink-0" />
                      <div>
                        <span className="font-semibold text-slate-800">{src.document}</span>
                        {src.section && (
                          <span className="text-slate-500 text-[11px]"> · {src.section}</span>
                        )}
                        {src.page && (
                          <span className="text-slate-400 text-[10px]"> (p. {src.page})</span>
                        )}
                      </div>
                      <span className="px-1.5 py-0.5 rounded text-[9.5px] font-mono uppercase bg-slate-100 text-slate-600 border border-slate-200 ml-1">
                        {src.category}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Retrieved Evidence Section (Accordion) */}
            {result.evidence && result.evidence.length > 0 && (
              <div className="border border-slate-200 rounded-xl overflow-hidden bg-white">
                <button
                  onClick={() => setShowEvidence(!showEvidence)}
                  className="w-full px-4 py-3 bg-slate-50/70 hover:bg-slate-50 flex items-center justify-between text-left transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-200 text-slate-700">
                      Knowledge Evidence
                    </span>
                    <span className="text-xs font-semibold text-slate-700">
                      Retrieved Chunks ({result.evidence.length})
                    </span>
                    <span className="text-[10px] text-slate-400 italic">
                      — Extracted from text corpus, NOT image rasters
                    </span>
                  </div>
                  {showEvidence ? (
                    <ChevronUp size={15} className="text-slate-400" />
                  ) : (
                    <ChevronDown size={15} className="text-slate-400" />
                  )}
                </button>

                {showEvidence && (
                  <div className="p-4 space-y-3 border-t border-slate-200 bg-white">
                    {result.evidence.map((ev, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-lg bg-slate-50/70 border border-slate-200/80 space-y-1.5 text-xs text-slate-700"
                      >
                        <div className="flex items-center justify-between text-[11px] text-slate-500">
                          <span className="font-semibold text-[#234238] flex items-center gap-1">
                            <FileText size={12} />
                            {ev.source}
                            {ev.section && ` › ${ev.section}`}
                          </span>
                          <span className="font-mono text-[10.5px] px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                            Similarity: {(ev.score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <p className="text-slate-700 leading-relaxed font-body bg-white p-2.5 rounded border border-slate-100">
                          &ldquo;{ev.text}&rdquo;
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
