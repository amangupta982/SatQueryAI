import { useCallback, useRef, useState } from 'react'
import { UploadCloud, ImageIcon, X, Sparkles, Loader2 } from 'lucide-react'

const ACCEPTED = ['image/jpeg', 'image/png', 'image/tiff', 'image/tif']

export default function ImageUploader({ onAnalyze }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [progress, setProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)

  const handleFiles = useCallback((files) => {
    const f = files?.[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    simulateUpload()
  }, [])

  const simulateUpload = () => {
    setUploading(true)
    setProgress(0)
    let p = 0
    const interval = setInterval(() => {
      p += Math.random() * 22 + 10
      if (p >= 100) {
        p = 100
        clearInterval(interval)
        setUploading(false)
      }
      setProgress(Math.round(p))
    }, 180)
  }

  const handleAnalyze = () => {
    setAnalyzing(true)
    setTimeout(() => {
      setAnalyzing(false)
      onAnalyze?.(file)
    }, 1800)
  }

  const removeFile = () => {
    setFile(null)
    setPreview(null)
    setProgress(0)
  }

  const dims = file ? '4096 × 4096 px' : null
  const sizeMb = file ? (file.size / (1024 * 1024)).toFixed(1) : null

  if (!file) {
    return (
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          handleFiles(e.dataTransfer.files)
        }}
        className={`relative flex flex-col items-center justify-center text-center rounded-xl border-2 border-dashed p-10 transition-colors cursor-pointer ${
          dragOver ? 'border-cyan-accent bg-cyan-accent/[0.04]' : 'border-white/[0.12] hover:border-white/[0.2] bg-white/[0.015]'
        }`}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.tif,.tiff"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="w-14 h-14 rounded-full bg-cyan-accent/10 border border-cyan-accent/25 flex items-center justify-center mb-4">
          <UploadCloud size={24} className="text-cyan-accent" strokeWidth={1.6} />
        </div>
        <h3 className="font-display font-semibold text-slate-100 text-base mb-1">Upload Remote Sensing Image</h3>
        <p className="text-sm text-slate-500">Drag & drop your satellite image here</p>
        <p className="text-sm text-slate-600 mb-4">
          or <span className="text-cyan-soft font-medium">browse from your computer</span>
        </p>
        <div className="flex items-center gap-2 text-[11px] text-slate-600 font-mono">
          <span className="px-2 py-0.5 rounded border border-white/[0.08]">JPG</span>
          <span className="px-2 py-0.5 rounded border border-white/[0.08]">PNG</span>
          <span className="px-2 py-0.5 rounded border border-white/[0.08]">TIFF</span>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-white/[0.08] bg-white/[0.015] p-4">
      <div className="flex gap-4">
        <div className="w-20 h-20 rounded-lg overflow-hidden border border-white/[0.08] shrink-0 bg-base-800">
          <img src={preview} alt="Preview" className="w-full h-full object-cover" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="text-sm font-medium text-slate-200 truncate flex items-center gap-1.5">
                <ImageIcon size={13} className="text-slate-500 shrink-0" />
                {file.name}
              </p>
              <p className="text-[11px] text-slate-500 mt-0.5 font-mono">
                {sizeMb} MB · {dims}
              </p>
            </div>
            <button onClick={removeFile} className="text-slate-500 hover:text-signal-rose shrink-0">
              <X size={16} />
            </button>
          </div>

          {uploading ? (
            <div className="mt-3">
              <div className="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                <div
                  className="h-full bg-cyan-accent transition-all duration-200"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5 font-mono">Uploading… {progress}%</p>
            </div>
          ) : (
            <div className="flex items-center gap-2 mt-3">
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan-accent text-base-950 text-xs font-semibold hover:bg-cyan-soft transition-colors disabled:opacity-70"
              >
                {analyzing ? <Loader2 size={13} className="animate-spin" /> : <Sparkles size={13} />}
                {analyzing ? 'Analyzing…' : 'Analyze Image'}
              </button>
              <button
                onClick={removeFile}
                className="px-3 py-1.5 rounded-lg border border-white/[0.1] text-xs text-slate-400 hover:text-slate-200 hover:bg-white/[0.05]"
              >
                Remove
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
