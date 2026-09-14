import { useState, useMemo, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Upload,
  Sparkles,
  Plus,
  X,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Boxes,
  Scan,
  Radio,
  FileText,
  ChevronDown,
  ChevronUp,
  Image as ImageIcon,
  ArrowRight,
  Database,
  Crosshair,
  Compass,
  Info,
} from 'lucide-react'
import { samplePresetDatasets, recentAnalyses, structuredAnalysisResults } from '../data/mockData'
import RAGKnowledgeCard from '../components/RAGKnowledgeCard'

export default function NewAnalysis() {
  const navigate = useNavigate()
  const location = useLocation()
  const fileInputRef = useRef(null)

  // ==========================================
  // STATE: IMAGERY & SCENES
  // ==========================================
  // Default to River Urban Expansion preset
  const defaultPreset = samplePresetDatasets['river-urban-expansion']
  const [uploadedScenes, setUploadedScenes] = useState(defaultPreset.scenes)
  const [queryText, setQueryText] = useState(defaultPreset.defaultQuery)
  const [activePresetKey, setActivePresetKey] = useState('river-urban-expansion')

  // Load from location state if passed from another page (e.g. Datasets or History)
  useEffect(() => {
    if (location.state?.presetQuery) {
      setQueryText(location.state.presetQuery)
    }
  }, [location.state])

  // Smooth scroll to RAG section if hash is #rag-knowledge
  useEffect(() => {
    if (location.hash === '#rag-knowledge') {
      const timer = setTimeout(() => {
        const el = document.getElementById('rag-knowledge')
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 150)
      return () => clearTimeout(timer)
    }
  }, [location.hash])

  // Accordion state for Optional Analysis Options
  const [optionsOpen, setOptionsOpen] = useState(false)
  const [roiActive, setRoiActive] = useState(false)
  const [coRegistration, setCoRegistration] = useState('auto')

  // ==========================================
  // STATE: WORKFLOW (setup | processing)
  // ==========================================
  const [workflowStage, setWorkflowStage] = useState('setup') // 'setup' | 'processing'
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [processingCheckpoints, setProcessingCheckpoints] = useState([
    { id: 1, name: 'Imagery validation & CRS calibration', status: 'pending' },
    { id: 2, name: 'Natural-language query parsing & entity extraction', status: 'pending' },
    { id: 3, name: 'Automatic task & model routing', status: 'pending' },
    { id: 4, name: 'Deep remote-sensing model execution', status: 'pending' },
    { id: 5, name: 'Raster evidence mask & vector delineation', status: 'pending' },
    { id: 6, name: 'Scientific interpretation synthesis', status: 'pending' },
  ])

  // Notification Toast
  const [toastMessage, setToastMessage] = useState(null)
  const showToast = (msg) => {
    setToastMessage(msg)
    setTimeout(() => setToastMessage(null), 3000)
  }

  // ==========================================
  // PRESET SELECTION HANDLER
  // ==========================================
  const handleSelectPreset = (presetKey) => {
    const preset = samplePresetDatasets[presetKey]
    if (!preset) return
    setActivePresetKey(presetKey)
    setUploadedScenes(preset.scenes)
    setQueryText(preset.defaultQuery)
    showToast(`Loaded sample dataset: ${preset.name}`)
  }

  // ==========================================
  // UPLOAD & REMOVE HANDLERS
  // ==========================================
  const handleRemoveScene = (sceneId) => {
    setUploadedScenes((prev) => prev.filter((s) => s.id !== sceneId))
    setActivePresetKey(null)
  }

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return

    const newScenes = files.map((file, idx) => {
      const isSAR = file.name.toLowerCase().includes('sar') || file.name.toLowerCase().includes('radar')
      return {
        id: `user-scene-${Date.now()}-${idx}`,
        name: file.name.replace(/\.[^/.]+$/, ''),
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        sensor: isSAR ? 'RISAT-1A (C-Band SAR)' : 'Sentinel-2 (Optical)',
        modality: isSAR ? 'SAR' : 'Optical',
        resolution: isSAR ? '3.0 m' : '10 m',
        dimensions: '1024 × 1024',
        bands: isSAR ? 'Dual-Pol (HH+HV)' : '4 bands (RGB + NIR)',
        preview: URL.createObjectURL(file),
      }
    })

    setUploadedScenes((prev) => [...prev, ...newScenes])
    setActivePresetKey(null)
    showToast(`Added ${files.length} satellite scene${files.length > 1 ? 's' : ''}`)
  }

  // ==========================================
  // DYNAMIC AUTOMATIC CAPABILITY DETECTION
  // ==========================================
  const detectedPlan = useMemo(() => {
    const q = queryText.toLowerCase().trim()
    const sceneCount = uploadedScenes.length
    const hasSAR = uploadedScenes.some((s) => s.modality === 'SAR')
    const hasOptical = uploadedScenes.some((s) => s.modality === 'Optical')

    // 1. Optical + SAR Multimodal
    if (hasSAR || (hasOptical && hasSAR) || q.includes('sar') || q.includes('radar') || q.includes('multimodal') || q.includes('flood')) {
      return {
        task: 'Optical + SAR',
        targetResultId: 'flooded-area-2026',
        description: 'Combine optical multispectral reflectance with microwave SAR backscatter for all-weather flood & water penetration.',
        reason: hasSAR
          ? 'SAR imagery detected in uploaded scenes; applying multimodal fusion.'
          : 'Query requests radar / flood analysis; routing to C-band SAR pipeline.',
        inputs: ['Optical multispectral pass ✓', 'C-Band SAR pass ✓', 'Co-registered bounding area ✓'],
        output: 'Fused inundation mask, specular backscatter stats, flood extent',
        estimatedTime: '~ 15–30 seconds',
        icon: Radio,
        color: 'text-indigo-600',
        badgeBg: 'bg-indigo-50 border-indigo-200 text-indigo-700',
      }
    }

    // 2. Change Analysis (2+ temporal optical scenes or query mentions change/expansion/growth)
    if (
      sceneCount >= 2 ||
      q.includes('change') ||
      q.includes('expansion') ||
      q.includes('between') ||
      q.includes('over time') ||
      q.includes('difference') ||
      q.includes('growth') ||
      q.includes('increase') ||
      q.includes('decrease')
    ) {
      return {
        task: 'Change Analysis',
        targetResultId: 'urban-expansion-2026',
        description: 'Compare two temporal satellite scenes to detect and quantify land-cover changes and structural expansion.',
        reason:
          sceneCount >= 2
            ? 'Multi-temporal scenes provided; comparing baseline T0 with T1.'
            : 'Temporal difference intent recognized from query semantics.',
        inputs: ['Scene 1 (T0 Baseline) ✓', 'Scene 2 (T1 Follow-up) ✓', 'Sub-pixel co-registration ✓'],
        output: 'Thematic change mask, NDBI/NDVI delta, change percentage, area stats',
        estimatedTime: '~ 10–25 seconds',
        icon: RotateCcw,
        color: 'text-rose-600',
        badgeBg: 'bg-rose-50 border-rose-200 text-rose-700',
      }
    }

    // 3. Object Detection / Grounding
    if (
      q.includes('detect') ||
      q.includes('count') ||
      q.includes('building') ||
      q.includes('structure') ||
      q.includes('road') ||
      q.includes('vehicle') ||
      q.includes('find') ||
      q.includes('locate') ||
      q.includes('box') ||
      q.includes('grounding')
    ) {
      return {
        task: 'Object Detection',
        targetResultId: 'buildings-near-river-2026',
        description: 'Identify and delineate discrete spatial objects, buildings, and civil infrastructure with bounding boxes.',
        reason: 'Structural counting and object localization query detected.',
        inputs: ['High-resolution optical scene ✓', 'Spatial bounding coordinates ✓'],
        output: 'Bounding boxes, class labels, spatial coordinates, confidence scores',
        estimatedTime: '~ 5–15 seconds',
        icon: Boxes,
        color: 'text-[#234238]',
        badgeBg: 'bg-[#e2eae5] border-[#c8d4ce] text-[#234238]',
      }
    }

    // 4. Default: Visual Question Answering (VQA)
    return {
      task: 'Visual Question Answering',
      targetResultId: 'vqa-sample',
      description: 'Perform multimodal visual question answering directly over complex Earth observation scenes.',
      reason: 'General spatial reasoning inquiry parsed from query.',
      inputs: ['Calibrated satellite scene ✓', 'Natural-language query embedding ✓'],
      output: 'Scientific text answer, spectral evidence markers, spatial focus',
      estimatedTime: '~ 3–10 seconds',
      icon: Scan,
      color: 'text-emerald-600',
      badgeBg: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    }
  }, [queryText, uploadedScenes])

  // ==========================================
  // EXECUTE ANALYSIS WORKFLOW
  // ==========================================
  const handleRunAnalysis = () => {
    if (uploadedScenes.length === 0) {
      showToast('Please upload at least one satellite scene.')
      return
    }
    if (!queryText.trim()) {
      showToast('Please enter an analysis query.')
      return
    }

    // Enter Processing State
    setWorkflowStage('processing')
    setElapsedSeconds(0)

    // Reset and simulate real scientific pipeline stages
    const checkpoints = [
      { id: 1, name: 'Imagery validation & CRS calibration', delay: 400 },
      { id: 2, name: 'Natural-language query parsing & entity extraction', delay: 900 },
      { id: 3, name: `Automatic routing to ${detectedPlan.task} pipeline`, delay: 1400 },
      { id: 4, name: 'Deep remote-sensing model execution', delay: 2100 },
      { id: 5, name: 'Raster evidence mask & vector delineation', delay: 2800 },
      { id: 6, name: 'Scientific interpretation synthesis', delay: 3400 },
    ]

    checkpoints.forEach((cp, idx) => {
      setTimeout(() => {
        setProcessingCheckpoints((prev) =>
          prev.map((item) => {
            if (item.id === cp.id) return { ...item, status: 'completed' }
            if (item.id === cp.id + 1) return { ...item, status: 'running' }
            return item
          })
        )
      }, cp.delay)
    })

    // Navigate to dedicated results workspace after completion
    setTimeout(() => {
      navigate(`/analyses/${detectedPlan.targetResultId}`, {
        state: {
          resultId: detectedPlan.targetResultId,
          query: queryText,
          scenes: uploadedScenes,
        },
      })
    }, 3900)
  }

  // Timer ticker during processing
  useEffect(() => {
    let timer
    if (workflowStage === 'processing') {
      timer = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1)
      }, 1000)
    }
    return () => clearInterval(timer)
  }, [workflowStage])

  // ============================================================
  // RENDER STATE B: SCIENTIFIC PROCESSING SCREEN
  // ============================================================
  if (workflowStage === 'processing') {
    return (
      <div className="flex-1 overflow-y-auto bg-[#fafaf8] flex items-center justify-center p-4 text-[#162721]">
        <div className="bg-white rounded-2xl border border-[#e5ebe7] p-6 md:p-8 max-w-xl w-full shadow-lg space-y-6 animate-fadeUp">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold text-[#234238] font-mono mb-1">
                <span className="w-2 h-2 rounded-full bg-[#234238] animate-pulse" />
                <span>ANALYSIS IN PROGRESS</span>
              </div>
              <h2 className="font-display font-bold text-lg text-[#162721]">
                Executing {detectedPlan.task} Pipeline
              </h2>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono text-slate-400 block">Elapsed Time</span>
              <span className="text-sm font-bold font-mono text-slate-800">
                {elapsedSeconds}.4s
              </span>
            </div>
          </div>

          {/* Active Query Banner */}
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-700">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Active Request
            </span>
            <p className="font-medium font-body italic">&ldquo;{queryText}&rdquo;</p>
          </div>

          {/* Pipeline Stage Checkpoints */}
          <div className="space-y-2.5">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Automated Checkpoints
            </span>
            <div className="space-y-2">
              {processingCheckpoints.map((cp) => (
                <div
                  key={cp.id}
                  className={`p-3 rounded-lg border flex items-center justify-between text-xs transition-all ${
                    cp.status === 'completed'
                      ? 'bg-emerald-50/60 border-emerald-200/80 text-emerald-900'
                      : cp.status === 'running'
                      ? 'bg-[#e2eae5] border-[#c8d4ce] text-[#234238] ring-1 ring-[#c8d4ce]'
                      : 'bg-slate-50/50 border-slate-200/60 text-slate-400'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    {cp.status === 'completed' && (
                      <CheckCircle2 size={15} className="text-emerald-600 shrink-0" />
                    )}
                    {cp.status === 'running' && (
                      <span className="w-3.5 h-3.5 rounded-full border-2 border-[#234238] border-t-transparent animate-spin shrink-0" />
                    )}
                    {cp.status === 'pending' && (
                      <span className="w-3.5 h-3.5 rounded-full border border-slate-300 shrink-0" />
                    )}
                    <span className="font-medium">{cp.name}</span>
                  </div>

                  <span className="text-[10.5px] font-mono capitalize">
                    {cp.status === 'running' ? 'Active' : cp.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <p className="text-center text-[11.5px] text-slate-400">
            SatQuery is routing imagery tensors to ISRO GPU nodes...
          </p>
        </div>
      </div>
    )
  }

  // ============================================================
  // RENDER STATE A: PROFESSIONAL INTERACTIVE SETUP WORKSPACE
  // ============================================================
  return (
    <div className="flex-1 overflow-y-auto bg-[#fafaf8] px-4 py-5 md:px-8 lg:px-12 text-[#162721] selection:bg-[#dce7e1] selection:text-[#162721]">
      <div className="max-w-7xl mx-auto space-y-6 pb-12">
        {/* Floating Toast Notification */}
        {toastMessage && (
          <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-slate-900 text-white text-xs font-medium px-4 py-3 rounded-xl shadow-2xl border border-slate-700 animate-fadeUp">
            <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
        )}

        {/* ============================================================ */}
        {/* HERO BANNER: SCIENTIFIC EARTH OBSERVATION HEADER             */}
        {/* ============================================================ */}
        <div className="relative rounded-2xl overflow-hidden border border-[#e4ebe6] shadow-sm bg-[#162721] text-white p-6 md:p-8">
          {/* Authentic Geographic Map / Satellite Texture Overlay */}
          <div
            className="absolute inset-0 opacity-40 mix-blend-luminosity pointer-events-none bg-cover bg-center"
            style={{
              backgroundImage: `url('/hero_brahmaputra_exact_seamless.jpg')`,
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#162721]/95 via-[#162721]/80 to-transparent pointer-events-none" />

          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <h1 className="font-display font-extrabold text-2xl sm:text-3xl lg:text-4xl tracking-tight text-white">
                Analyze the Earth with AI
              </h1>
              <p className="text-xs sm:text-sm text-[#d0e0d6] leading-relaxed font-body">
                Upload satellite imagery, ask a question, and let SatQuery automatically select the right analysis to give you accurate, evidence-based insights.
              </p>

              {/* 4 Compact Capability Badges */}
              <div className="flex items-center gap-2 pt-2 flex-wrap">
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/10 backdrop-blur-xs border border-white/15 text-xs font-medium text-white hover:bg-white/15 transition-colors">
                  <Scan size={13} className="text-emerald-400" />
                  <span>Visual Question Answering</span>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/10 backdrop-blur-xs border border-white/15 text-xs font-medium text-white hover:bg-white/15 transition-colors">
                  <Boxes size={13} className="text-teal-300" />
                  <span>Object Detection</span>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/10 backdrop-blur-xs border border-white/15 text-xs font-medium text-white hover:bg-white/15 transition-colors">
                  <RotateCcw size={13} className="text-rose-300" />
                  <span>Change Analysis</span>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/10 backdrop-blur-xs border border-white/15 text-xs font-medium text-white hover:bg-white/15 transition-colors">
                  <Layers size={13} className="text-emerald-300" />
                  <span>Optical + SAR</span>
                </div>
              </div>
            </div>

            {/* Right Tagline */}
            <div className="hidden lg:block text-right shrink-0 border-l border-white/15 pl-6">
              <p className="text-xs font-semibold text-[#a1b8ac] uppercase tracking-wider">
                Turning Satellite Data into
              </p>
              <p className="font-display font-bold text-lg text-[#9cd1b8] mt-0.5">
                Real-World Insight
              </p>
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* TWO-COLUMN WORKSPACE: IMAGERY (LEFT) + REQUEST (RIGHT)       */}
        {/* ============================================================ */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* ========================================== */}
          {/* LEFT COLUMN: IMAGERY (DOMINANT 7/12)      */}
          {/* ========================================== */}
          <div className="lg:col-span-7 space-y-6">
            {/* 1. Upload Satellite Imagery Container */}
            <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-display font-bold text-sm text-slate-900">
                    1. Upload Satellite Imagery
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Add one or more satellite scenes (optical, SAR, or both)
                  </p>
                </div>

                {/* Sample Data Quick Selector */}
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-medium text-[#63766c] hidden sm:inline">
                    Sample Data:
                  </span>
                  <button
                    onClick={() => handleSelectPreset('river-urban-expansion')}
                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg border transition-all ${
                      activePresetKey === 'river-urban-expansion'
                        ? 'bg-[#234238] border-[#234238] text-white shadow-xs'
                        : 'bg-white border-[#d8e0dc] text-[#5d6f66] hover:bg-[#f2f6f3]'
                    }`}
                  >
                    River Expansion
                  </button>
                  <button
                    onClick={() => handleSelectPreset('river-buildings-grounding')}
                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg border transition-all ${
                      activePresetKey === 'river-buildings-grounding'
                        ? 'bg-[#234238] border-[#234238] text-white shadow-xs'
                        : 'bg-white border-[#d8e0dc] text-[#5d6f66] hover:bg-[#f2f6f3]'
                    }`}
                  >
                    Buildings
                  </button>
                  <button
                    onClick={() => handleSelectPreset('flood-sar-inundation')}
                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg border transition-all ${
                      activePresetKey === 'flood-sar-inundation'
                        ? 'bg-[#234238] border-[#234238] text-white shadow-xs'
                        : 'bg-white border-[#d8e0dc] text-[#5d6f66] hover:bg-[#f2f6f3]'
                    }`}
                  >
                    Flood SAR
                  </button>
                </div>
              </div>

              {/* Grid of Scene Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {uploadedScenes.map((scene) => (
                  <div
                    key={scene.id}
                    className="group relative rounded-xl border border-slate-200/90 bg-white overflow-hidden shadow-xs hover:border-slate-300 transition-all flex flex-col"
                  >
                    {/* Scene Image Preview */}
                    <div className="relative aspect-[16/10] bg-slate-900 overflow-hidden">
                      <img
                        src={scene.preview}
                        alt={scene.name}
                        className="w-full h-full object-cover group-hover:scale-102 transition-transform duration-300"
                      />

                      {/* Top Overlay Bar */}
                      <div className="absolute top-2 left-2 right-2 flex items-center justify-between text-white text-xs">
                        <span className="font-semibold px-2 py-0.5 rounded bg-slate-900/80 backdrop-blur-xs text-[11px]">
                          {scene.name}
                        </span>
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono text-[10.5px] px-1.5 py-0.5 rounded bg-slate-900/70">
                            {scene.date}
                          </span>
                          <button
                            onClick={() => handleRemoveScene(scene.id)}
                            className="p-1 rounded-full bg-slate-900/80 hover:bg-rose-600 transition-colors"
                            title="Remove scene"
                          >
                            <X size={12} />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Compact Scene Metadata Footer */}
                    <div className="p-3 bg-slate-50/60 border-t border-slate-100 space-y-1 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-800 text-[12px] truncate">
                          {scene.sensor}
                        </span>
                        <span
                          className={`text-[10px] font-semibold px-1.5 py-0.2 rounded border ${
                            scene.modality === 'SAR'
                              ? 'bg-purple-50 text-purple-700 border-purple-200'
                              : 'bg-[#e2eae5] text-[#234238] border-[#c8d4ce]'
                          }`}
                        >
                          {scene.modality}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                        <span>{scene.dimensions}</span>
                        <span>{scene.resolution}</span>
                        <span>{scene.bands}</span>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Add More Images Drag-and-Drop Card */}
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="rounded-xl border-2 border-dashed border-[#d8e0dc] hover:border-[#234238] bg-slate-50/50 hover:bg-[#234238]/5 p-5 flex flex-col items-center justify-center text-center cursor-pointer transition-all min-h-[190px] space-y-2"
                >
                  <div className="w-10 h-10 rounded-full bg-[#e2eae5] text-[#234238] flex items-center justify-center border border-[#c8d4ce]">
                    <Plus size={18} strokeWidth={2.4} />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-800">Add More Images</p>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      Drag & drop or <span className="text-[#234238] font-semibold underline">browse</span>
                    </p>
                  </div>
                  <p className="text-[10px] text-slate-400 max-w-[200px] leading-tight font-mono">
                    Supports GeoTIFF, TIFF, JP2, PNG, JPG (Multi-image supported)
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".tif,.tiff,.jp2,.png,.jpg,.jpeg"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>
              </div>
            </div>

            {/* Recent Analyses Section */}
            <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-display font-bold text-sm text-slate-900">Recent Analyses</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Your past analyses and results</p>
                </div>
                <button
                  onClick={() => navigate('/history')}
                  className="text-xs font-semibold text-[#234238] hover:text-[#1a342c] flex items-center gap-1"
                >
                  <span>View All</span>
                  <ArrowRight size={13} />
                </button>
              </div>

              {/* 3 Compact Recent Analysis Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {recentAnalyses.map((rec) => (
                  <div
                    key={rec.id}
                    onClick={() => navigate(`/analyses/${rec.id}`)}
                    className="group rounded-xl border border-slate-200/90 bg-white hover:border-[#234238]/40 hover:shadow-sm p-3 flex flex-col justify-between cursor-pointer transition-all space-y-2.5"
                  >
                    <div className="relative aspect-[16/10] rounded-lg overflow-hidden bg-slate-900">
                      <img
                        src={rec.thumbnail}
                        alt={rec.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      />
                      <span className="absolute top-1.5 left-1.5 text-[9.5px] font-semibold px-2 py-0.5 rounded bg-slate-900/80 text-white backdrop-blur-xs">
                        {rec.task}
                      </span>
                    </div>

                    <div>
                      <h4 className="font-semibold text-slate-900 text-xs group-hover:text-[#234238] transition-colors">
                        {rec.title}
                      </h4>
                      <p className="text-[10.5px] text-slate-400 font-mono mt-0.5">
                        {rec.date} · {rec.imageCount} {rec.imageCount > 1 ? 'images' : 'image'}
                      </p>
                      <p className="text-[11px] text-slate-600 mt-1 line-clamp-2 leading-relaxed">
                        {rec.summary}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ========================================== */}
          {/* RIGHT COLUMN: REQUEST & PLAN (5/12)       */}
          {/* ========================================== */}
          <div className="lg:col-span-5 space-y-4">
            {/* 2. Ask SatQuery Section */}
            <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-3">
              <div>
                <h2 className="font-display font-bold text-sm text-slate-900">2. Ask SatQuery</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Describe what you want to know about the imagery
                </p>
              </div>

              {/* Large Textarea */}
              <div className="relative">
                <textarea
                  rows={4}
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value.slice(0, 500))}
                  placeholder="What would you like to know about this imagery?"
                  className="w-full p-3.5 text-xs text-slate-800 bg-slate-50/70 hover:bg-slate-50 focus:bg-white border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#234238]/20 focus:border-[#234238] transition-all font-body resize-none leading-relaxed"
                />
                <div className="flex items-center justify-between text-[11px] text-slate-400 px-1 pt-1 font-mono">
                  <div className="flex items-center gap-1">
                    <ImageIcon size={12} className="text-slate-400" />
                    <span>{uploadedScenes.length} scenes attached</span>
                  </div>
                  <span>{queryText.length}/500</span>
                </div>
              </div>

              {/* Example Prompts Pills */}
              <div className="pt-1 flex items-center gap-1.5 flex-wrap">
                <span className="text-[10.5px] font-semibold text-slate-400 uppercase">Try:</span>
                <button
                  onClick={() =>
                    setQueryText('What changed in the built-up area near the river between these two images?')
                  }
                  className="text-[11px] px-2 py-0.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
                >
                  River expansion
                </button>
                <button
                  onClick={() => setQueryText('Detect and delineate all building structures in this sector.')}
                  className="text-[11px] px-2 py-0.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
                >
                  Building detection
                </button>
                <button
                  onClick={() => setQueryText('Identify flood inundation using optical and SAR microwave data.')}
                  className="text-[11px] px-2 py-0.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
                >
                  Flood SAR
                </button>
              </div>
            </div>

            {/* AI Analysis Plan (Compact & Dynamic) */}
            <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-3.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Sparkles size={14} className="text-[#234238]" />
                  <span className="font-display font-bold text-xs text-slate-900 uppercase tracking-wider">
                    AI Analysis Plan
                  </span>
                </div>
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span>Auto-detected</span>
                </span>
              </div>

              {/* Selected Method Details */}
              <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200 space-y-2">
                <div className="flex items-center gap-2">
                  <div className={`p-1.5 rounded-lg bg-white border border-slate-200 ${detectedPlan.color}`}>
                    <detectedPlan.icon size={15} />
                  </div>
                  <div>
                    <h4 className="font-display font-bold text-sm text-slate-900">
                      {detectedPlan.task}
                    </h4>
                    <p className="text-[11px] text-slate-500 leading-tight">
                      {detectedPlan.description}
                    </p>
                  </div>
                </div>

                <p className="text-[11px] text-slate-600 bg-white p-2 rounded-lg border border-slate-200/80">
                  <span className="font-semibold text-slate-700">Reasoning: </span>
                  {detectedPlan.reason}
                </p>

                {/* Checklist of inputs */}
                <div className="space-y-1 pt-1 text-xs text-slate-600 font-mono">
                  <div className="text-[10px] font-bold uppercase text-slate-400 font-sans tracking-wider">
                    Required Inputs
                  </div>
                  {detectedPlan.inputs.map((inp, idx) => (
                    <div key={idx} className="flex items-center gap-1.5">
                      <span className="text-emerald-600">✓</span>
                      <span>{inp}</span>
                    </div>
                  ))}
                </div>

                {/* Output expectations */}
                <div className="pt-1 text-[11.5px]">
                  <span className="text-[10px] font-bold uppercase text-slate-400 block tracking-wider font-sans">
                    Expected Evidence
                  </span>
                  <span className="text-slate-700">{detectedPlan.output}</span>
                </div>

                {/* Estimated processing time */}
                <div className="flex items-center gap-1 text-[11px] text-slate-500 pt-1 font-mono">
                  <Clock size={12} />
                  <span>Estimated Time: {detectedPlan.estimatedTime}</span>
                </div>
              </div>

              {/* PRIMARY ACTION: RUN ANALYSIS BUTTON */}
              <button
                onClick={handleRunAnalysis}
                className="w-full py-3 bg-[#234238] hover:bg-[#1a342c] text-white font-semibold text-xs rounded-xl shadow-md shadow-[#234238]/20 transition-all flex items-center justify-center gap-2 group cursor-pointer"
              >
                <Play size={14} className="fill-white group-hover:translate-x-0.5 transition-transform" />
                <span>Run Analysis</span>
              </button>

              <p className="text-center text-[11px] text-slate-400">
                SatQuery will automatically select the best model and tools
              </p>
            </div>

            {/* Analysis Options (Optional) - Collapsible Accordion */}
            <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
              <button
                onClick={() => setOptionsOpen(!optionsOpen)}
                className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
                  <Crosshair size={14} className="text-slate-500" />
                  <span>Analysis Options (Optional)</span>
                </div>
                {optionsOpen ? <ChevronUp size={15} className="text-slate-400" /> : <ChevronDown size={15} className="text-slate-400" />}
              </button>

              {optionsOpen && (
                <div className="px-4 pb-4 pt-1 border-t border-slate-100 space-y-3 text-xs">
                  {/* Region of Interest */}
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-slate-800 text-xs">Region of Interest (ROI)</p>
                      <p className="text-[11px] text-slate-500">Draw a bounding polygon on the imagery</p>
                    </div>
                    <button
                      onClick={() => {
                        setRoiActive(!roiActive)
                        showToast(roiActive ? 'ROI drawing cleared' : 'Click imagery to delineate ROI')
                      }}
                      className={`px-3 py-1 text-xs font-semibold rounded-lg border transition-all ${
                        roiActive
                          ? 'bg-[#234238] text-white border-[#234238]'
                          : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      {roiActive ? 'ROI Active ✓' : 'Draw ROI'}
                    </button>
                  </div>

                  {/* Sensor Alignment */}
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
                    <p className="font-semibold text-slate-800 text-xs">Sensor Co-Registration</p>
                    <p className="text-[11px] text-slate-500">
                      Sub-pixel orthorectification alignment algorithm
                    </p>
                    <div className="flex items-center gap-2 pt-1">
                      <label className="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
                        <input
                          type="radio"
                          name="coreg"
                          checked={coRegistration === 'auto'}
                          onChange={() => setCoRegistration('auto')}
                          className="accent-[#234238]"
                        />
                        <span>Automatic (Recommended)</span>
                      </label>
                      <label className="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer ml-3">
                        <input
                          type="radio"
                          name="coreg"
                          checked={coRegistration === 'manual'}
                          onChange={() => setCoRegistration('manual')}
                          className="accent-[#234238]"
                        />
                        <span>Manual GCPs</span>
                      </label>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* RAG / REMOTE SENSING DOMAIN KNOWLEDGE SECTION                */}
        {/* ============================================================ */}
        <RAGKnowledgeCard />

        {/* ============================================================ */}
        {/* FOOTER                                                        */}
        {/* ============================================================ */}
        <div className="pt-6 border-t border-slate-200/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <div className="text-[#234238]">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M12 2a4 4 0 0 0-4 4c0 2.5 4 6 4 6s4-3.5 4-6a4 4 0 0 0-4-4Z" />
                <path d="M12 22a4 4 0 0 0 4-4c0-2.5-4-6-4-6s-4 3.5-4 6a4 4 0 0 0 4 4Z" />
                <path d="M2 12a4 4 0 0 0 4 4c2.5 0 6-4 6-4s-3.5-4-6-4a4 4 0 0 0-4 4Z" />
                <path d="M22 12a4 4 0 0 0-4-4c-2.5 0-6 4-6 4s3.5 4 6 4a4 4 0 0 0 4 4Z" />
              </svg>
            </div>
            <span className="font-semibold text-slate-700">SatQuery AI</span>
            <span>— Satellite Intelligence for a Better Tomorrow</span>
          </div>

          <div className="flex items-center gap-4 text-[11px] font-medium">
            <span className="hover:text-slate-800 cursor-pointer">About</span>
            <span className="hover:text-slate-800 cursor-pointer">Documentation</span>
            <span className="hover:text-slate-800 cursor-pointer">Contact</span>
            <span className="text-slate-300">|</span>
            <span className="text-slate-600 font-mono">Built for Research · v0.1.0</span>
          </div>
        </div>
      </div>
    </div>
  )
}
