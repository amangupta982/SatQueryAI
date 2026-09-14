import { jsPDF } from 'jspdf'

/**
 * Loads any image source (URL, blob URL, or data URI) and converts it to a base64 JPEG data URL.
 */
async function getBase64Image(src) {
  if (!src) return null
  if (typeof src === 'string' && src.startsWith('data:image/')) {
    return src
  }
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'Anonymous'
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        canvas.width = img.naturalWidth || img.width || 600
        canvas.height = img.naturalHeight || img.height || 400
        const ctx = canvas.getContext('2d')
        ctx.fillStyle = '#ffffff'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(img, 0, 0)
        resolve(canvas.toDataURL('image/jpeg', 0.85))
      } catch (e) {
        console.warn('Canvas conversion failed for report image:', e)
        resolve(null)
      }
    }
    img.onerror = () => {
      console.warn('Could not load image for report:', src)
      resolve(null)
    }
    img.src = src
  })
}

/**
 * Professional SatQuery AI PDF Report Generator.
 *
 * @param {Object} reportData
 * @param {string} reportData.title - Report Title
 * @param {string} reportData.analysisType - e.g. "Visual Question Answering (VQA)", "Area Measurement & Segmentation", "Change Intelligence", "Optical-SAR Multimodal Fusion"
 * @param {string} [reportData.query] - User task or question
 * @param {string} [reportData.modelUsed] - Model name / backbone
 * @param {string} [reportData.prediction] - Main prediction answer text
 * @param {number|string} [reportData.confidence] - Confidence score or percentage (optional, omitted if null/undefined)
 * @param {Object} [reportData.sceneDetails] - Key/value pairs describing scene (location, sensor, resolution, dates, filename)
 * @param {Array<{ label: string, value: string|number }>} [reportData.statistics] - Quantitative findings
 * @param {Array<{ name: string, percent?: number|string, areaHa?: number|string, change?: number|string, extra?: string }>} [reportData.categories] - Category breakdown
 * @param {Array<{ title: string, src: string }>} [reportData.evidenceImages] - Visual evidence images to embed
 * @param {string} [reportData.limitations] - Sensor or resolution limitations
 * @param {string} [reportData.executionNotes] - Runtime details or notes
 * @param {string} [reportData.fileName] - Suggested filename for download
 */
export async function generatePredictionReport(reportData) {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  })

  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 14
  const contentWidth = pageWidth - margin * 2

  let y = margin

  // Helper to ensure enough vertical space or add a page
  const checkPageBreak = (neededHeight) => {
    if (y + neededHeight > pageHeight - 16) {
      doc.addPage()
      y = margin + 4
      drawPageHeader()
    }
  }

  // Draw subtle top header on subsequent pages
  const drawPageHeader = () => {
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(8)
    doc.setTextColor(110, 125, 118)
    doc.text('SatQuery AI — Prediction & Intelligence Report', margin, y)
    doc.text(reportData.analysisType || 'Earth Observation Analysis', pageWidth - margin, y, { align: 'right' })
    y += 3
    doc.setDrawColor(226, 232, 228)
    doc.setLineWidth(0.3)
    doc.line(margin, y, pageWidth - margin, y)
    y += 6
  }

  // ── 1. SatQuery AI Header Banner ──
  // Top green banner background
  doc.setFillColor(35, 66, 56) // Deep Forest Green (#234238)
  doc.roundedRect(margin, y, contentWidth, 22, 2, 2, 'F')

  // Brand Name & Subtitle
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(15)
  doc.setTextColor(255, 255, 255)
  doc.text('SatQuery AI', margin + 6, y + 9)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(8.5)
  doc.setTextColor(205, 220, 212)
  doc.text('Satellite Intelligence & Earth Observation Prediction System', margin + 6, y + 15)

  // Report Type Badge & Date on Right
  const dateStr = new Date().toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(9)
  doc.setTextColor(255, 255, 255)
  doc.text(reportData.analysisType || 'ANALYSIS REPORT', pageWidth - margin - 6, y + 9, { align: 'right' })

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(7.5)
  doc.setTextColor(190, 205, 198)
  doc.text(`Generated: ${dateStr}`, pageWidth - margin - 6, y + 15, { align: 'right' })

  y += 28

  // ── 2. Analysis Metadata Grid ──
  doc.setFillColor(250, 250, 248) // #fafaf8 cream
  doc.setDrawColor(229, 235, 231) // #e5ebe7
  doc.setLineWidth(0.3)

  const metaRows = []
  if (reportData.modelUsed) metaRows.push({ label: 'Model Backbone', val: reportData.modelUsed })
  if (reportData.confidence !== null && reportData.confidence !== undefined) {
    const confVal = typeof reportData.confidence === 'number'
      ? `${(reportData.confidence > 1 ? reportData.confidence : reportData.confidence * 100).toFixed(1)}%`
      : String(reportData.confidence)
    metaRows.push({ label: 'Confidence', val: confVal })
  }
  if (reportData.sceneDetails) {
    Object.entries(reportData.sceneDetails).forEach(([k, v]) => {
      if (v) metaRows.push({ label: k, val: String(v) })
    })
  }

  if (metaRows.length > 0) {
    const metaBoxHeight = Math.ceil(metaRows.length / 2) * 6 + 7
    doc.roundedRect(margin, y, contentWidth, metaBoxHeight, 1.5, 1.5, 'FD')

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(7.5)
    doc.setTextColor(107, 124, 115) // #6b7c73
    doc.text('SCENE & EXECUTION METADATA', margin + 4, y + 4.5)

    let rowY = y + 9
    metaRows.forEach((item, idx) => {
      const colX = idx % 2 === 0 ? margin + 4 : margin + contentWidth / 2 + 2
      if (idx % 2 === 0 && idx > 0) rowY += 6

      doc.setFont('helvetica', 'normal')
      doc.setFontSize(8)
      doc.setTextColor(100, 115, 107)
      doc.text(`${item.label}:`, colX, rowY)

      doc.setFont('helvetica', 'bold')
      doc.setTextColor(22, 39, 33)
      const labelW = doc.getTextWidth(`${item.label}: `)
      doc.text(item.val, colX + labelW, rowY)
    })

    y += metaBoxHeight + 6
  }

  // ── 3. Query / Task (if available) ──
  if (reportData.query) {
    checkPageBreak(18)
    doc.setFillColor(244, 247, 245)
    doc.setDrawColor(220, 231, 225)
    doc.roundedRect(margin, y, contentWidth, 13, 1.5, 1.5, 'FD')

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(8)
    doc.setTextColor(45, 82, 67)
    doc.text('USER TASK / QUERY:', margin + 4, y + 5)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(8.5)
    doc.setTextColor(22, 39, 33)
    const queryLines = doc.splitTextToSize(reportData.query, contentWidth - 42)
    doc.text(queryLines[0] || reportData.query, margin + 38, y + 5)

    y += 18
  }

  // ── 4. Primary Prediction / Answer ──
  if (reportData.prediction) {
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(9)
    doc.setTextColor(35, 66, 56)
    doc.text('FINAL PREDICTION & INTELLIGENCE SUMMARY', margin, y)
    y += 4

    const answerLines = doc.splitTextToSize(reportData.prediction, contentWidth - 8)
    const boxHeight = Math.max(16, answerLines.length * 4.5 + 8)

    checkPageBreak(boxHeight + 4)

    // Callout box with deep forest green left accent
    doc.setFillColor(248, 250, 249)
    doc.setDrawColor(220, 230, 224)
    doc.roundedRect(margin, y, contentWidth, boxHeight, 1.5, 1.5, 'FD')

    doc.setFillColor(35, 66, 56)
    doc.rect(margin, y, 2.5, boxHeight, 'F')

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.setTextColor(22, 39, 33)
    doc.text(answerLines, margin + 6, y + 6)

    y += boxHeight + 7
  }

  // ── 5. Relevant Statistics (Key-Value Badges) ──
  if (reportData.statistics && reportData.statistics.length > 0) {
    checkPageBreak(24)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(9)
    doc.setTextColor(35, 66, 56)
    doc.text('QUANTITATIVE FINDINGS & METRICS', margin, y)
    y += 4

    const statCount = reportData.statistics.length
    const statW = (contentWidth - (statCount - 1) * 3) / statCount
    const statH = 14

    reportData.statistics.forEach((stat, idx) => {
      const sx = margin + idx * (statW + 3)
      doc.setFillColor(250, 250, 248)
      doc.setDrawColor(229, 235, 231)
      doc.roundedRect(sx, y, statW, statH, 1.5, 1.5, 'FD')

      doc.setFont('helvetica', 'normal')
      doc.setFontSize(7.5)
      doc.setTextColor(110, 125, 118)
      doc.text(stat.label, sx + 3, y + 5)

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(9.5)
      doc.setTextColor(35, 66, 56)
      doc.text(String(stat.value), sx + 3, y + 10.5)
    })

    y += statH + 7
  }

  // ── 6. Category / Class Breakdown Table (if available) ──
  if (reportData.categories && reportData.categories.length > 0) {
    const tableHeaderHeight = 6
    const rowHeight = 5.5
    const totalTableHeight = tableHeaderHeight + reportData.categories.length * rowHeight + 8

    checkPageBreak(Math.min(totalTableHeight, 40))

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(9)
    doc.setTextColor(35, 66, 56)
    doc.text('LAND COVER / REGIONAL CLASSIFICATION BREAKDOWN', margin, y)
    y += 4

    // Table Header
    doc.setFillColor(235, 242, 238) // #ebf2ee
    doc.setDrawColor(220, 230, 224)
    doc.rect(margin, y, contentWidth, tableHeaderHeight, 'FD')

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(7.5)
    doc.setTextColor(35, 66, 56)
    doc.text('CLASS / CATEGORY', margin + 4, y + 4.2)
    doc.text('PROPORTION', margin + 65, y + 4.2)
    doc.text('PHYSICAL AREA (HA)', margin + 110, y + 4.2)
    doc.text('DYNAMIC / NOTES', margin + 145, y + 4.2)
    y += tableHeaderHeight

    // Table Rows
    reportData.categories.forEach((cat, idx) => {
      checkPageBreak(rowHeight + 2)
      doc.setFillColor(idx % 2 === 0 ? 255 : 250, idx % 2 === 0 ? 255 : 250, idx % 2 === 0 ? 255 : 248)
      doc.setDrawColor(235, 240, 237)
      doc.rect(margin, y, contentWidth, rowHeight, 'FD')

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(8)
      doc.setTextColor(22, 39, 33)
      doc.text(cat.name, margin + 4, y + 3.8)

      doc.setFont('helvetica', 'normal')
      doc.setTextColor(60, 75, 68)
      const pctStr = cat.percent !== undefined && cat.percent !== null ? `${cat.percent}%` : '—'
      doc.text(pctStr, margin + 65, y + 3.8)

      const areaStr = cat.areaHa !== undefined && cat.areaHa !== null ? `${cat.areaHa} ha` : '—'
      doc.text(areaStr, margin + 110, y + 3.8)

      const noteStr = cat.change || cat.extra || 'Stable'
      doc.text(noteStr, margin + 145, y + 3.8)

      y += rowHeight
    })

    y += 6
  }

  // ── 7. Visual Evidence (Embedded Images) ──
  if (reportData.evidenceImages && reportData.evidenceImages.length > 0) {
    checkPageBreak(60)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(9)
    doc.setTextColor(35, 66, 56)
    doc.text('VISUAL EVIDENCE & PERCEPTION OVERLAYS', margin, y)
    y += 4

    for (const ev of reportData.evidenceImages) {
      if (!ev.src) continue
      try {
        const base64 = await getBase64Image(ev.src)
        if (base64) {
          const imgW = 82
          const imgH = 50
          checkPageBreak(imgH + 12)

          doc.setFillColor(250, 250, 248)
          doc.setDrawColor(229, 235, 231)
          doc.roundedRect(margin, y, contentWidth, imgH + 8, 1.5, 1.5, 'FD')

          doc.addImage(base64, 'JPEG', margin + 3, y + 3, imgW, imgH)

          // Caption & description on the right side
          doc.setFont('helvetica', 'bold')
          doc.setFontSize(8.5)
          doc.setTextColor(35, 66, 56)
          doc.text(ev.title || 'Visual Evidence Layer', margin + imgW + 8, y + 10)

          doc.setFont('helvetica', 'normal')
          doc.setFontSize(7.5)
          doc.setTextColor(110, 125, 118)
          doc.text('Foundation model segmentation overlay', margin + imgW + 8, y + 16)
          doc.text('with deterministic coordinates.', margin + imgW + 8, y + 21)

          if (ev.details) {
            doc.text(ev.details, margin + imgW + 8, y + 28)
          }

          y += imgH + 12
        }
      } catch (err) {
        console.warn('Could not add image to report:', err)
      }
    }
  }

  // ── 8. Limitations & Execution Notes ──
  if (reportData.limitations || reportData.executionNotes) {
    checkPageBreak(22)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(8)
    doc.setTextColor(120, 100, 70)
    doc.text('OPERATIONAL LIMITATIONS & METHODOLOGY NOTES', margin, y)
    y += 4

    const notes = [reportData.limitations, reportData.executionNotes].filter(Boolean).join(' • ')
    const noteLines = doc.splitTextToSize(notes, contentWidth - 8)
    const noteBoxH = Math.max(12, noteLines.length * 4 + 6)

    doc.setFillColor(253, 248, 240) // soft cream
    doc.setDrawColor(236, 228, 214)
    doc.roundedRect(margin, y, contentWidth, noteBoxH, 1.5, 1.5, 'FD')

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(7.5)
    doc.setTextColor(130, 95, 45)
    doc.text(noteLines, margin + 4, y + 5)

    y += noteBoxH + 6
  }

  // ── Page Numbering & Bottom Footer (for all pages) ──
  const totalPages = doc.internal.getNumberOfPages()
  for (let p = 1; p <= totalPages; p++) {
    doc.setPage(p)
    doc.setDrawColor(229, 235, 231)
    doc.setLineWidth(0.3)
    doc.line(margin, pageHeight - 11, pageWidth - margin, pageHeight - 11)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(7)
    doc.setTextColor(125, 140, 133)
    doc.text(
      'SatQuery AI • Earth Observation Intelligence Platform • Confidential Research Document',
      margin,
      pageHeight - 7
    )
    doc.text(`Page ${p} of ${totalPages}`, pageWidth - margin, pageHeight - 7, { align: 'right' })
  }

  // Download the generated PDF
  const defaultFilename = `SatQueryAI_${(reportData.analysisType || 'Prediction').replace(/\s+/g, '_')}_${Date.now()}.pdf`
  doc.save(reportData.fileName || defaultFilename)
}
