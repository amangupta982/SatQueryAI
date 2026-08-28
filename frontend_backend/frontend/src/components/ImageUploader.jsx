import { useCallback, useRef, useState } from 'react'
import { UploadCloud, ImageIcon, X, Sparkles, Loader2, Plus, GitCompare, FileImage } from 'lucide-react'

export default function ImageUploader({ onAnalyze, isCompareMode, onToggleCompareMode }) {
  const inputRef = useRef(null)
  const addMoreRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [analyzing, setAnalyzing] = useState(false)

  const processFiles = useCallback((newFilesList) => {
    if (!newFilesList || newFilesList.length === 0) return

    const incoming = Array.from(newFilesList).map((f) => ({
      id: crypto.randomUUID(),
      file: f,
      name: f.name,
      sizeMb: (f.size / (1024 * 1024)).toFixed(1),
      preview: URL.createObjectURL(f),
      dims: '4096 × 4096 px',
    }))

    setFiles((prev) => [...prev, ...incoming])
    simulateUpload()
  }, [])

  const simulateUpload = () => {
    setUploading(true)
    setProgress(0)
    let p = 0
    const interval = setInterval(() => {
      p += Math.random() * 25 + 15
      if (p >= 100) {
        p = 100
        clearInterval(interval)
        setUploading(false)
      }
      setProgress(Math.round(p))
    }, 120)
  }

  const removeFile = (id) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  const handleAnalyze = () => {
    setAnalyzing(true)
    setTimeout(() => {
      setAnalyzing(false)
      onAnalyze?.(files, isCompareMode)
    }, 1800)
  }

  return (
    <div className="space-y-4">
      {/* Hidden file inputs */}
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".jpg,.jpeg,.png,.tif,.tiff"
        className="hidden"
        onChange={(e) => processFiles(e.target.files)}
      />
      <input
        ref={addMoreRef}
        type="file"
        multiple
        accept=".jpg,.jpeg,.png,.tif,.tiff"
        className="hidden"
        onChange={(e) => processFiles(e.target.files)}
      />

      {files.length === 0 ? (
        /* Empty Drag & Drop Zone */
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragOver(true)
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragOver(false)
            processFiles(e.dataTransfer.files)
          }}
          onClick={() => inputRef.current?.click()}
          className={`relative flex flex-col items-center justify-center text-center rounded-2xl border-2 border-dashed p-10 transition-all cursor-pointer ${
            dragOver
              ? 'border-blue-500 bg-blue-50/50 scale-[0.99]'
              : 'border-slate-300 hover:border-blue-400 bg-white hover:bg-slate-50/50 shadow-xs'
          }`}
        >
          <div className="w-14 h-14 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center mb-4 text-blue-600">
            <UploadCloud size={26} strokeWidth={1.8} />
          </div>
          <h3 className="font-display font-bold text-slate-900 text-base mb-1">
            {isCompareMode ? 'Upload Two or More Images to Compare' : 'Upload Remote Sensing Imagery'}
          </h3>
          <p className="text-sm text-slate-500">
            Drag & drop one or multiple satellite scenes here
          </p>
          <p className="text-sm text-slate-500 mb-4">
            or <span className="text-blue-600 font-semibold underline underline-offset-2">browse files</span>
          </p>
          <div className="flex items-center gap-2 text-[11px] text-slate-500 font-mono">
            <span className="px-2.5 py-0.5 rounded-lg border border-slate-200 bg-slate-50">JPG</span>
            <span className="px-2.5 py-0.5 rounded-lg border border-slate-200 bg-slate-50">PNG</span>
            <span className="px-2.5 py-0.5 rounded-lg border border-slate-200 bg-slate-50">TIFF</span>
            <span className="px-2.5 py-0.5 rounded-lg border border-blue-200 bg-blue-50 text-blue-600 font-medium">Multi-image Support</span>
          </div>
        </div>
      ) : (
        /* List / Grid of Uploaded Images */
        <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <FileImage size={16} className="text-blue-600" />
              <p className="text-xs font-bold text-slate-800">
                Uploaded Imagery ({files.length} {files.length === 1 ? 'scene' : 'scenes'})
              </p>
            </div>
            <button
              onClick={() => addMoreRef.current?.click()}
              className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200 transition-colors"
            >
              <Plus size={13} strokeWidth={2.5} />
              <span>Add More</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {files.map((item, index) => (
              <div
                key={item.id}
                className="flex items-center gap-3 p-2.5 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-slate-50 transition-colors relative group"
              >
                <div className="w-14 h-14 rounded-lg overflow-hidden border border-slate-200 bg-slate-100 shrink-0">
                  <img src={item.preview} alt={item.name} className="w-full h-full object-cover" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1 text-[11px] font-semibold text-slate-700">
                    <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold flex items-center justify-center shrink-0">
                      {index + 1}
                    </span>
                    <span className="truncate">{item.name}</span>
                  </div>
                  <p className="text-[10.5px] text-slate-500 mt-0.5 font-mono">
                    {item.sizeMb} MB · {item.dims}
                  </p>
                </div>
                <button
                  onClick={() => removeFile(item.id)}
                  title="Remove image"
                  className="p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                >
                  <X size={15} />
                </button>
              </div>
            ))}
          </div>

          {uploading ? (
            <div className="pt-2">
              <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full bg-blue-600 transition-all duration-200 rounded-full"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5 font-mono">Uploading images… {progress}%</p>
            </div>
          ) : (
            <div className="flex items-center justify-between pt-2 border-t border-slate-100 gap-3">
              <div className="flex items-center gap-2">
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing || files.length === 0}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 transition-colors disabled:opacity-60 shadow-xs"
                >
                  {analyzing ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : isCompareMode || files.length > 1 ? (
                    <GitCompare size={14} />
                  ) : (
                    <Sparkles size={14} />
                  )}
                  <span>
                    {analyzing
                      ? 'Processing Analysis…'
                      : isCompareMode || files.length > 1
                      ? `Compare & Analyze (${files.length} Images)`
                      : 'Analyze Image'}
                  </span>
                </button>

                <button
                  onClick={() => setFiles([])}
                  className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
                >
                  Clear All
                </button>
              </div>

              {files.length >= 2 && (
                <span className="text-[11px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-1 rounded-lg font-medium">
                  ✓ Comparison Ready
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
