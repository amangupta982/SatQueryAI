import { useState } from 'react'
import { FileDown, Loader2 } from 'lucide-react'
import { generatePredictionReport } from '../services/reportGenerator'

/**
 * Reusable Download Prediction Report Button Component.
 *
 * @param {Object} props
 * @param {Object|Function} props.reportData - The data object to feed into reportGenerator, OR an async function returning the report data object.
 * @param {string} [props.className] - Optional custom CSS classes.
 * @param {string} [props.label] - Custom button label, defaults to "Download Prediction Report".
 * @param {string} [props.variant] - "primary" (forest green) or "secondary" (outline cream). Defaults to "primary".
 */
export default function DownloadReportButton({
  reportData,
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
      const data = typeof reportData === 'function' ? await reportData() : reportData
      if (!data) {
        console.warn('No report data provided for PDF generation')
        return
      }
      await generatePredictionReport(data)
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
