import { useState } from 'react'
import { FileDown, Loader2 } from 'lucide-react'
import { generatePredictionReport } from '../services/reportGenerator'

/**
 * Reusable Download Prediction Report Button Component.
 *
 * @param {Object} props
 * @param {Object|Function} [props.reportData] - The data object or function returning report data.
 * @param {Object} [props.analysisData] - Alternative alias for reportData.
 * @param {string} [props.className] - Optional custom CSS classes.
 * @param {string} [props.label] - Custom button label, defaults to "Download Prediction Report".
 * @param {string} [props.variant] - "primary" (forest green), "secondary" (outline cream), or "dark". Defaults to "primary".
 */
export default function DownloadReportButton({
  reportData,
  analysisData,
  className = '',
  label = 'Download Prediction Report',
  variant = 'primary',
}) {
  const [generating, setGenerating] = useState(false)

  const handleDownload = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (generating) return

    setGenerating(true)
    try {
      const raw = typeof reportData === 'function' ? await reportData() : (reportData || analysisData)
      if (!raw) {
        console.warn('No report data provided for PDF generation')
        return
      }

      // Automatically normalize into generatePredictionReport format
      const formatted = {
        title: raw.title || `${raw.intent || raw.task || 'SatQuery AI'} Analysis Report`,
        analysisType: raw.analysisType || raw.task || raw.intent || 'Earth Observation Analysis',
        query: raw.query || '',
        modelUsed: raw.modelUsed || raw.modelName || (Array.isArray(raw.agentsUsed) ? raw.agentsUsed.join(', ') : 'SatQuery AI Orchestrator'),
        prediction: raw.prediction || raw.interpretation || raw.answer || 'Analysis complete.',
        confidence: raw.confidence !== undefined ? raw.confidence : raw.confidence_display,
        sceneDetails: raw.sceneDetails || {
          'Analysis Task': raw.task || raw.intent || 'Change Detection',
          'Execution Status': 'Completed',
          'Model Pipeline': raw.modelName || (Array.isArray(raw.agentsUsed) ? raw.agentsUsed.join(', ') : 'SatQuery AI Multimodal Ensemble'),
        },
        statistics: raw.statistics || (raw.metrics ? raw.metrics.map(m => ({ label: m.label, value: m.value })) : undefined),
        evidenceImages: raw.evidenceImages || (raw.imageEvidence ? raw.imageEvidence.map(ev => ({
          title: ev.title || 'Visual Evidence',
          src: ev.url_or_b64 || ev.url || ev.file_path,
        })) : undefined),
        categories: raw.categories,
        fileName: raw.fileName || `SatQueryAI_${(raw.task || raw.intent || 'Prediction').replace(/[^a-zA-Z0-9_-]/g, '_')}_${Date.now()}.pdf`,
      }

      // If raw has images dict (from structuredForUi):
      if (!formatted.evidenceImages && raw.images) {
        formatted.evidenceImages = []
        if (raw.images.result) formatted.evidenceImages.push({ title: 'Result Overlay', src: raw.images.result })
        if (raw.images.before) formatted.evidenceImages.push({ title: 'Before Scene (T1)', src: raw.images.before })
        if (raw.images.after) formatted.evidenceImages.push({ title: 'After Scene (T2)', src: raw.images.after })
      }

      await generatePredictionReport(formatted)
    } catch (err) {
      console.error('Failed to generate PDF report:', err)
      alert('Could not generate PDF report. Please check console for details.')
    } finally {
      setGenerating(false)
    }
  }

  const baseStyles =
    'inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold shadow-2xs transition-all cursor-pointer select-none disabled:opacity-50'

  const variantStyles =
    variant === 'secondary'
      ? 'bg-white hover:bg-[#f4f7f5] text-[#234238] border border-[#c8d5cc]'
      : variant === 'dark'
      ? 'bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700'
      : 'bg-[#234238] hover:bg-[#1a342c] text-white'

  return (
    <button
      type="button"
      onClick={handleDownload}
      disabled={generating}
      className={`${baseStyles} ${variantStyles} ${className}`}
      title="Download publication-grade Earth Observation Prediction Report in PDF format"
    >
      {generating ? (
        <>
          <Loader2 size={14} className="animate-spin text-current" />
          <span>Generating PDF...</span>
        </>
      ) : (
        <>
          <FileDown size={14} strokeWidth={2} />
          <span>{label}</span>
        </>
      )}
    </button>
  )
}
