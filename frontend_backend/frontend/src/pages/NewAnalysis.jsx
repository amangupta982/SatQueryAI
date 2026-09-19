import { useState, useMemo, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Bot,
  User,
  Send,
  Paperclip,
  Sparkles,
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
  Crosshair,
  ExternalLink,
  Copy,
  Check,
  Trash2,
  Pin,
  Pencil,
  X,
  MoreVertical,
  Maximize2,
  Info,
  ShieldCheck,
  Compass,
  Plus,
  Building2,
  Leaf,
  Droplets,
  MessageSquare,
  PenTool,
  RefreshCw,
  Sparkle,
  Globe2,
} from 'lucide-react'
import { samplePresetDatasets } from '../data/mockData'
import DownloadReportButton from '../components/DownloadReportButton'
import EarthScene from '../components/EarthScene'
import ChangeIntelligenceStudio from '../components/ChangeIntelligenceStudio'

// Suggested analysis cards on hero landing (Dark Glassmorphic Edition)
const suggestedCards = [
  {
    id: 'buildings',
    title: 'Detect Buildings',
    desc: 'Find and map structures in satellite images',
    icon: Building2,
    iconBg: 'bg-blue-600/30 border border-blue-500/40 text-blue-300',
    query: 'Detect and count all building structures and waterfront infrastructure in this satellite imagery.',
    presetKey: 'river-buildings-grounding',
  },
  {
    id: 'landcover',
    title: 'Analyze Land Cover',
    desc: 'Classify and measure land use',
    icon: Leaf,
    iconBg: 'bg-emerald-600/30 border border-emerald-500/40 text-emerald-300',
    query: 'What is the land-cover area and coverage measurement for this image?',
    presetKey: 'river-urban-expansion',
  },
  {
    id: 'water',
    title: 'Measure Water',
    desc: 'Analyze water bodies and surface area',
    icon: Droplets,
    iconBg: 'bg-cyan-600/30 border border-cyan-500/40 text-cyan-300',
    query: 'What percentage of this area is water and surface water bodies?',
    presetKey: 'flood-sar-inundation',
  },
  {
    id: 'compare',
    title: 'Compare Images',
    desc: 'Detect changes over time',
    icon: Layers,
    iconBg: 'bg-teal-600/30 border border-teal-500/40 text-teal-300',
    query: 'What changed in the built-up area and landscape between these two images?',
    presetKey: 'river-urban-expansion',
  },
]

// Quick prompt pills below input
const quickPromptPills = [
  'How many buildings are visible?',
  'What percentage is water?',
  'Analyze land cover',
  'Compare two images',
]

// Default recent analyses list matching dark mockup
const defaultRecentAnalyses = [
  {
    id: 'recent-1',
    title: 'River Flood Assessment',
    date: 'Sep 15, 2026',
    thumb: '/dark_thumb1.jpg',
    query: 'Identify water-covered regions and flood extent along the river course.',
    presetKey: 'flood-sar-inundation',
    isPinned: true, // pin first item by default for great demonstration
  },
  {
    id: 'recent-2',
    title: 'Urban Expansion',
    date: 'Sep 12, 2026',
    thumb: '/dark_thumb2.jpg',
    query: 'Detect and count all building structures and infrastructure along the riverbank.',
    presetKey: 'river-buildings-grounding',
    isPinned: false,
  },
  {
    id: 'recent-3',
    title: 'Forest Change',
    date: 'Sep 08, 2026',
    thumb: '/dark_thumb3.jpg',
    query: 'What changed in the forest and vegetation coverage between these two images?',
    presetKey: 'river-urban-expansion',
    isPinned: false,
  },
  {
    id: 'recent-4',
    title: 'Land Cover Analysis',
    date: 'Sep 05, 2026',
    thumb: '/dark_thumb4.jpg',
    query: 'Calculate land-cover area coverage and land use distribution.',
    presetKey: 'river-urban-expansion',
    isPinned: false,
  },
  {
    id: 'recent-5',
    title: 'Coastal Monitoring',
    date: 'Sep 01, 2026',
    thumb: '/dark_thumb5.jpg',
    query: 'Examine coastline boundary dynamics, port infrastructure, and offshore features.',
    presetKey: 'river-buildings-grounding',
    isPinned: false,
  },
]

export default function NewAnalysis() {
  const navigate = useNavigate()
  const location = useLocation()
  const fileInputRef = useRef(null)
  const chatBottomRef = useRef(null)
  const textareaRef = useRef(null)
  const heroInputRef = useRef(null)

  // ==========================================
  // STATE: IMAGERY & ACTIVE PRESET
  // ==========================================
  const defaultPresetKey = 'river-urban-expansion'
  const defaultPreset = samplePresetDatasets[defaultPresetKey]

  const [uploadedScenes, setUploadedScenes] = useState([])
  const [activePresetKey, setActivePresetKey] = useState(null)
  const [activeNavMode, setActiveNavMode] = useState('chat') // 'chat', 'image', 'change', 'area', '3d'

  // ==========================================
  // STATE: CHAT CONVERSATION STREAM
  // ==========================================
  const [queryInput, setQueryInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [copiedIndex, setCopiedIndex] = useState(null)
  const [expandedTraceIndex, setExpandedTraceIndex] = useState(null)
  const [toastMessage, setToastMessage] = useState(null)

  const showToast = (msg) => {
    setToastMessage(msg)
    setTimeout(() => setToastMessage(null), 3000)
  }

  // ==========================================
  // STATE: RECENT ANALYSES HISTORY (PIN, EDIT, DELETE)
  // ==========================================
  const [analysesHistory, setAnalysesHistory] = useState(() => {
    try {
      const saved = localStorage.getItem('satquery_analyses_history')
      if (saved) return JSON.parse(saved)
    } catch (e) {
      console.warn('Failed to parse saved history:', e)
    }
    return defaultRecentAnalyses
  })

  // Persist history changes to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('satquery_analyses_history', JSON.stringify(analysesHistory))
    } catch (e) {
      console.warn('Failed to save history to localStorage:', e)
    }
  }, [analysesHistory])

  // Renaming state
  const [editingId, setEditingId] = useState(null)
  const [editingTitle, setEditingTitle] = useState('')

  // Sorted list: Pinned items always appear at the top
  const sortedHistory = useMemo(() => {
    return [...analysesHistory].sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1
      if (!a.isPinned && b.isPinned) return 1
      return 0
    })
  }, [analysesHistory])

  // Toggle Pin / Unpin
  const handleTogglePin = (id, e) => {
    e?.stopPropagation()
    setAnalysesHistory((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, isPinned: !item.isPinned } : item
      )
    )
    const target = analysesHistory.find((i) => i.id === id)
    showToast(target?.isPinned ? 'Unpinned analysis' : 'Pinned analysis to top')
  }

  // Start Renaming
  const handleStartRename = (item, e) => {
    e?.stopPropagation()
    setEditingId(item.id)
    setEditingTitle(item.title)
  }

  // Save Renaming
  const handleSaveRename = (id, e) => {
    e?.stopPropagation()
    const trimmed = editingTitle.trim()
    if (!trimmed) {
      setEditingId(null)
      return
    }
    setAnalysesHistory((prev) =>
      prev.map((item) => (item.id === id ? { ...item, title: trimmed } : item))
    )
    showToast('Renamed analysis successfully')
    setEditingId(null)
  }

  // Cancel Renaming
  const handleCancelRename = (e) => {
    e?.stopPropagation()
    setEditingId(null)
    setEditingTitle('')
  }

  // Delete Chat / Analysis
  const handleDeleteChat = (id, e) => {
    e?.stopPropagation()
    setAnalysesHistory((prev) => prev.filter((item) => item.id !== id))
    showToast('Analysis deleted from history')
  }

  // Empty initial messages state so the user lands on the exact dark mockup hero view!
  const [messages, setMessages] = useState([])

  // Auto-scroll to bottom of chat on new messages
  useEffect(() => {
    if (messages.length > 0) {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, loading])

  // Handle location preset query if passed from navigation
  useEffect(() => {
    if (location.state?.presetQuery) {
      setQueryInput(location.state.presetQuery)
    }
  }, [location.state])

  // Auto-resize textarea in chat mode
  const handleTextareaChange = (e) => {
    setQueryInput(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`
    }
  }

  // ==========================================
  // HANDLERS: ATTACHMENTS & PRESETS
  // ==========================================
  const handleSelectPreset = (presetKey) => {
    const preset = samplePresetDatasets[presetKey]
    if (!preset) return
    setActivePresetKey(presetKey)
    setUploadedScenes(preset.scenes)
    showToast(`Loaded satellite preset: ${preset.name}`)
  }

  const processAndAttachFiles = async (files) => {
    if (!files || files.length === 0) return

    const readAsBase64 = (file) =>
      new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = () => resolve(null)
        reader.readAsDataURL(file)
      })

    const newScenes = await Promise.all(
      files.map(async (file, idx) => {
        const isSAR =
          file.name.toLowerCase().includes('sar') || file.name.toLowerCase().includes('radar')
        const b64 = await readAsBase64(file)
        return {
          id: `user-scene-${Date.now()}-${idx}`,
          name: file.name ? file.name.replace(/\.[^/.]+$/, '') : `Image-${idx + 1}`,
          date: new Date().toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          }),
          sensor: isSAR ? 'RISAT-1A (C-Band SAR)' : 'Sentinel-2 (Optical)',
          modality: isSAR ? 'SAR' : 'Optical',
          resolution: isSAR ? '3.0 m' : '10 m',
          dimensions: '1024 × 1024',
          bands: isSAR ? 'Dual-Pol (HH+HV)' : '4 bands (RGB + NIR)',
          preview: b64 || URL.createObjectURL(file),
          base64: b64,
          fileObj: file,
        }
      })
    )

    // When the user attaches their own imagery, append or use new scenes
    setUploadedScenes((prev) => (activePresetKey ? newScenes : [...prev, ...newScenes]))
    setActivePresetKey(null)
    showToast(`Attached ${files.length} satellite image${files.length > 1 ? 's' : ''}`)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files || [])
    processAndAttachFiles(files)
  }

  const handlePaste = (e) => {
    const items = e.clipboardData?.items
    if (!items) return
    const imageFiles = []
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile()
        if (file) imageFiles.push(file)
      }
    }
    if (imageFiles.length > 0) {
      e.preventDefault()
      processAndAttachFiles(imageFiles)
    }
  }

  const handleRemoveScene = (sceneId) => {
    setUploadedScenes((prev) => prev.filter((s) => s.id !== sceneId))
    setActivePresetKey(null)
  }

  const handleStartNewAnalysis = () => {
    setMessages([])
    setUploadedScenes([])
    setActivePresetKey(null)
    setQueryInput('')
    setActiveNavMode('chat')
    showToast('Ready for new analysis')
  }

  const handleClearChat = () => {
    setMessages([])
    showToast('Conversation cleared')
  }

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(idx)
    setTimeout(() => setCopiedIndex(null), 2000)
    showToast('Copied to clipboard')
  }

  // ==========================================
  // CORE: SEND MESSAGE TO ORCHESTRATOR
  // ==========================================
  const handleSendMessage = async (customText, optionalPresetKey = null) => {
    const q = (customText || queryInput).trim()
    if (!q || loading) return

    let currentScenes = [...uploadedScenes]
    let currentPreset = activePresetKey || optionalPresetKey

    // If no scenes are currently attached, load reference scene or preset
    if (currentScenes.length === 0 && optionalPresetKey) {
      const p = samplePresetDatasets[optionalPresetKey]
      if (p) {
        currentScenes = p.scenes
        currentPreset = optionalPresetKey
        setUploadedScenes(p.scenes)
        setActivePresetKey(optionalPresetKey)
      }
    }

    // 1. Append User Message
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      query: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      scenesAttached: currentScenes,
    }

    setMessages((prev) => [...prev, userMsg])
    setQueryInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    setLoading(true)

    try {
      // Gather image identifiers and representations
      let finalImageIds = []
      if (currentScenes.length > 0) {
        finalImageIds = currentScenes.map((s) => s.id || s.name)
      } else if (currentPreset && samplePresetDatasets[currentPreset]) {
        finalImageIds = samplePresetDatasets[currentPreset].scenes.map((s) => s.id)
      } else if (currentPreset) {
        finalImageIds = [currentPreset]
      } else {
        finalImageIds = ['bengaluru']
      }

      const timestamps = currentScenes.map((s) => s.date).filter(Boolean)
      const hasSAR = currentScenes.some((s) => s.modality === 'SAR')

      // Extract Base64 or Data URLs from attached scenes
      const imageB64s = currentScenes
        .map((s) => {
          if (s.base64) return s.base64
          if (s.preview && s.preview.startsWith('data:')) return s.preview
          return null
        })
        .filter(Boolean)

      const payload = {
        query: q,
        image_ids: finalImageIds,
        image_b64s: imageB64s.length > 0 ? imageB64s : undefined,
        timestamps: timestamps.length >= 2 ? timestamps : undefined,
        modality: hasSAR ? 'SAR' : 'Optical',
      }

      const res = await fetch('/api/orchestrator/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        throw new Error(`Orchestrator returned HTTP ${res.status}`)
      }

      const data = await res.json()

      // 2. Append Assistant Message with full orchestrator findings
      const assistantMsg = {
        id: `assist-${Date.now()}`,
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: data.intent,
        agentsUsed: data.agents_used || [],
        answer: data.answer,
        confidence: data.confidence_display || '89%',
        imageEvidence: data.image_evidence || [],
        knowledgeEvidence: data.knowledge_evidence || [],
        measurements: data.measurements || {},
        boundingBoxes: data.bounding_boxes || [],
        trace: data.trace,
        requiresClarification: data.requires_clarification,
        clarificationOptions: data.clarification_options,
        rawOrchestratorData: data,
        structuredForUi: data.structured_for_ui,
        changeData:
          data.change_data ||
          data.structured_for_ui?.changeData ||
          data.measurements?.change_data ||
          data.measurements?.change_detection_change_data ||
          null,
        attachedScenes: currentScenes.length > 0 ? currentScenes : uploadedScenes,
      }

      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      console.error('Orchestrator call error:', err)
      const errorMsg = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: 'System Notice',
        agentsUsed: ['SatQuery Orchestrator'],
        answer: `I encountered an issue processing your request: ${err.message || 'Connection to orchestrator failed'}. Please verify that the backend services are running.`,
        isError: true,
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full w-full bg-[#050b14] text-slate-100 overflow-hidden font-body selection:bg-cyan-500/30 selection:text-white">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-16 right-6 z-50 flex items-center gap-2.5 bg-slate-900/95 backdrop-blur-md text-white text-xs font-medium px-4 py-2.5 rounded-xl shadow-2xl border border-cyan-500/30 animate-fadeUp">
          <CheckCircle2 size={15} className="text-cyan-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Hidden file input for file selection */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,.tif,.tiff"
        className="hidden"
        onChange={handleFileUpload}
      />

      {/* ============================================================ */}
      {/* LEFT SIDEBAR (EXACT MATCH TO DARK MOCKUP)                     */}
      {/* ============================================================ */}
      <aside className="w-60 xl:w-64 h-full bg-[#07111e]/90 backdrop-blur-2xl border-r border-cyan-500/20 flex flex-col p-3.5 shrink-0 select-none overflow-y-auto z-20">
        {/* + New Analysis Button (Glowing Cyan Pill) */}
        <button
          onClick={handleStartNewAnalysis}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-[#5eead4] hover:bg-[#2dd4bf] text-slate-950 text-xs font-bold shadow-[0_0_20px_rgba(94,234,212,0.3)] transition-all cursor-pointer mb-4"
        >
          <Plus size={15} strokeWidth={2.8} />
          <span>New Analysis</span>
        </button>



        {/* Recent Analyses Section Header */}
        <div className="flex items-center justify-between px-1 mb-2">
          <span className="text-xs font-bold text-slate-300">Recent Analyses</span>
          <button
            onClick={() => navigate('/history')}
            className="text-[11px] font-medium text-slate-400 hover:text-cyan-300 transition-colors"
          >
            See all
          </button>
        </div>

        {/* Recent Analyses List with Thumbnails & Pin / Edit / Delete Actions */}
        <div className="space-y-1.5 overflow-y-auto mb-4 flex-1 pr-0.5">
          {sortedHistory.length === 0 ? (
            <div className="py-6 text-center text-slate-500 text-xs">
              No saved analyses
            </div>
          ) : (
            sortedHistory.map((item) => (
              <div
                key={item.id}
                className={`w-full group relative flex items-center gap-2 p-1.5 rounded-xl transition-all border ${
                  item.isPinned
                    ? 'bg-cyan-950/25 border-cyan-500/30'
                    : 'bg-transparent hover:bg-slate-800/50 border-transparent hover:border-cyan-500/20'
                }`}
              >
                {/* Clickable thumbnail to load preset */}
                <button
                  type="button"
                  onClick={() => {
                    handleSelectPreset(item.presetKey)
                    handleSendMessage(item.query, item.presetKey)
                    showToast(`Loaded: ${item.title}`)
                  }}
                  className="shrink-0 cursor-pointer focus:outline-none"
                  title={`Open ${item.title}`}
                >
                  <img
                    src={item.thumb}
                    alt={item.title}
                    className={`w-8 h-8 rounded-lg object-cover border shrink-0 transition-transform group-hover:scale-105 ${
                      item.isPinned ? 'border-cyan-400/60 shadow-[0_0_8px_rgba(56,189,248,0.25)]' : 'border-slate-700/80'
                    }`}
                  />
                </button>

                {/* Title & Metadata OR Inline Edit Form */}
                <div className="min-w-0 flex-1">
                  {editingId === item.id ? (
                    <div className="flex items-center gap-1 w-full" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveRename(item.id, e)
                          if (e.key === 'Escape') handleCancelRename(e)
                        }}
                        autoFocus
                        className="w-full bg-slate-950 border border-cyan-400 rounded px-1.5 py-0.5 text-xs text-white outline-none shadow-inner"
                      />
                      <button
                        type="button"
                        onClick={(e) => handleSaveRename(item.id, e)}
                        title="Save title"
                        className="p-1 rounded bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/40 cursor-pointer"
                      >
                        <Check size={12} strokeWidth={2.5} />
                      </button>
                      <button
                        type="button"
                        onClick={handleCancelRename}
                        title="Cancel"
                        className="p-1 rounded bg-slate-800 text-slate-400 hover:bg-slate-700 cursor-pointer"
                      >
                        <X size={12} strokeWidth={2.5} />
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => {
                        handleSelectPreset(item.presetKey)
                        handleSendMessage(item.query, item.presetKey)
                        showToast(`Loaded: ${item.title}`)
                      }}
                      className="w-full text-left focus:outline-none cursor-pointer"
                    >
                      <div className="flex items-center gap-1">
                        <p className="text-xs font-semibold text-slate-200 truncate group-hover:text-cyan-300 transition-colors">
                          {item.title}
                        </p>
                        {item.isPinned && (
                          <Pin size={10} className="text-cyan-400 fill-cyan-400 shrink-0 rotate-45" />
                        )}
                      </div>
                      <p className="text-[10px] text-slate-400">{item.date}</p>
                    </button>
                  )}
                </div>

                {/* Action Buttons: Pin, Edit Name, Delete (visible on hover) */}
                {editingId !== item.id && (
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5 shrink-0">
                    {/* Pin / Unpin Button */}
                    <button
                      type="button"
                      onClick={(e) => handleTogglePin(item.id, e)}
                      title={item.isPinned ? 'Unpin analysis' : 'Pin analysis to top'}
                      className={`p-1 rounded-md transition-colors cursor-pointer ${
                        item.isPinned
                          ? 'text-cyan-400 hover:bg-cyan-950/80'
                          : 'text-slate-400 hover:text-cyan-300 hover:bg-slate-700/60'
                      }`}
                    >
                      <Pin size={12} className={item.isPinned ? 'fill-cyan-400 rotate-45' : '-rotate-45'} />
                    </button>

                    {/* Rename Button */}
                    <button
                      type="button"
                      onClick={(e) => handleStartRename(item, e)}
                      title="Rename analysis"
                      className="p-1 rounded-md text-slate-400 hover:text-cyan-300 hover:bg-slate-700/60 transition-colors cursor-pointer"
                    >
                      <Pencil size={11} />
                    </button>

                    {/* Delete Button */}
                    <button
                      type="button"
                      onClick={(e) => handleDeleteChat(item.id, e)}
                      title="Delete analysis"
                      className="p-1 rounded-md text-slate-400 hover:text-red-400 hover:bg-red-500/20 transition-colors cursor-pointer"
                    >
                      <Trash2 size={11} />
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Bottom Promo Card (Dark Glassmorphic Edition) */}
        <div className="relative mt-auto rounded-2xl overflow-hidden border border-cyan-500/30 shadow-xl p-3 text-white flex flex-col justify-between min-h-[105px] bg-gradient-to-b from-blue-950/70 to-slate-950/90 group shrink-0">
          <div className="flex items-start gap-2.5 relative z-10">
            {/* Globe icon badge */}
            <div className="w-7 h-7 rounded-xl bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center text-cyan-300 shrink-0 shadow-[0_0_10px_rgba(56,189,248,0.2)]">
              <Globe2 size={15} />
            </div>

            <div className="min-w-0 flex-1">
              <h4 className="font-bold text-xs leading-tight tracking-tight text-white">
                Exploring<br />
                a Brighter Tomorrow
              </h4>
              <p className="text-[10px] text-slate-300 leading-snug mt-1 opacity-90">
                From space data<br />
                to real-world impact.
              </p>
            </div>
          </div>

          <div className="relative z-10 self-end mt-1">
            <button
              onClick={() => navigate('/datasets')}
              className="w-6 h-6 rounded-full bg-white text-slate-950 flex items-center justify-center hover:bg-cyan-200 shadow transition-transform group-hover:scale-110 cursor-pointer"
              title="Explore space datasets"
            >
              <ArrowRight size={12} strokeWidth={2.5} />
            </button>
          </div>
        </div>
      </aside>

      {/* ============================================================ */}
      {/* RIGHT MAIN WORKSPACE (ANIMATED ROTATING EARTH & SATELLITE)   */}
      {/* ============================================================ */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative bg-[#030712]">
        {messages.length === 0 ? (
          /* ========================================================== */
          /* 1. HERO LANDING VIEW (ANIMATED ROTATING EARTH & SATELLITE) */
          /* ========================================================== */
          <div className="relative flex-1 overflow-y-auto px-6 py-6 sm:px-10 md:px-14 lg:px-20 flex flex-col justify-between">
            {/* CELESTIAL BACKGROUND: 3D ROTATING EARTH GLOBE & MOVING SATELLITE (THREE.JS) */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
              {/* 3D Photorealistic Earth Scene */}
              <EarthScene />

              {/* Seamless Dark Vignette for Text & Card Contrast */}
              <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/20 to-black/85 pointer-events-none" />
            </div>


            {/* Main Central Content (Centered Horizontally) */}
            <div className="relative z-10 max-w-4xl mx-auto w-full pt-6 sm:pt-10 flex flex-col items-center text-center">
              {/* Eyebrow */}
              <div className="text-[11px] font-mono tracking-[0.25em] text-slate-300/80 font-semibold uppercase mb-3">
                FROM EARTH DATA TO MEANINGFUL INSIGHTS
              </div>

              {/* Main Headline (Centered, with 'analyze' in glowing electric blue) */}
              <h1 className="text-3xl sm:text-4xl lg:text-[46px] font-bold text-white tracking-tight leading-[1.12]">
                What would you like<br />
                to <span className="text-[#38bdf8] drop-shadow-[0_0_20px_rgba(56,189,248,0.5)]">analyze</span> today?
              </h1>

              {/* Subtitle */}
              <p className="text-xs sm:text-sm text-slate-300/90 mt-3 max-w-xl mx-auto leading-relaxed">
                Ask questions about satellite imagery, upload an image, or choose a suggested analysis.
              </p>

              {/* 4 Action Cards (Dark Glassmorphic in a Row) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 mt-8 w-full">
                {suggestedCards.map((card) => {
                  const Icon = card.icon
                  return (
                    <button
                      key={card.id}
                      onClick={() => handleSendMessage(card.query, card.presetKey)}
                      className="group text-left p-4 rounded-2xl bg-slate-950/50 backdrop-blur-md border border-white/10 hover:border-cyan-400/50 hover:bg-slate-900/70 p-4 flex flex-col justify-between h-36 transition-all duration-300 shadow-xl cursor-pointer"
                    >
                      <div>
                        <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${card.iconBg} shadow-sm`}>
                          <Icon size={18} strokeWidth={2} />
                        </div>
                        <h3 className="font-bold text-xs sm:text-sm text-white mt-3 group-hover:text-cyan-300 transition-colors">
                          {card.title}
                        </h3>
                        <p className="text-[11px] sm:text-xs text-slate-400 mt-1 leading-snug">
                          {card.desc}
                        </p>
                      </div>
                      <div className="self-end text-slate-400 group-hover:text-cyan-300 group-hover:translate-x-0.5 transition-all">
                        <ArrowRight size={15} />
                      </div>
                    </button>
                  )
                })}
              </div>

              {/* Central Search & Prompt Input Bar */}
              <div className="mt-8 w-full">
                {/* Attached images indicator pill if any */}
                {uploadedScenes.length > 0 && (
                  <div className="flex flex-wrap items-center justify-center gap-2 mb-2">
                    <span className="text-[11px] font-bold text-cyan-300 uppercase tracking-wider">
                      Attached ({uploadedScenes.length}):
                    </span>
                    {uploadedScenes.map((sc) => (
                      <div
                        key={sc.id}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-cyan-950/70 border border-cyan-500/40 text-xs text-cyan-200"
                      >
                        {sc.preview && (
                          <img src={sc.preview} alt={sc.name} className="w-4 h-4 rounded-xs object-cover" />
                        )}
                        <span className="max-w-[120px] truncate font-medium">{sc.name}</span>
                        <button
                          onClick={() => handleRemoveScene(sc.id)}
                          className="text-cyan-400 hover:text-white font-bold ml-1"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 hover:underline"
                    >
                      + Add Image
                    </button>
                  </div>
                )}

                <div className="rounded-2xl border border-cyan-500/35 bg-slate-950/65 backdrop-blur-xl shadow-2xl focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-500/25 flex items-center p-2 pl-4 transition-all">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="text-slate-300 hover:text-white p-1.5 rounded-lg transition-colors cursor-pointer mr-2 shrink-0"
                    title="Attach satellite imagery"
                  >
                    <Paperclip size={18} />
                  </button>
                  <input
                    ref={heroInputRef}
                    type="text"
                    value={queryInput}
                    onChange={(e) => setQueryInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleSendMessage()
                    }}
                    onPaste={handlePaste}
                    placeholder="Ask SatQuery AI about your imagery..."
                    className="flex-1 bg-transparent text-xs sm:text-sm text-white placeholder-slate-400 focus:outline-none"
                  />
                  <button
                    type="button"
                    disabled={!queryInput.trim() && uploadedScenes.length === 0}
                    onClick={() => handleSendMessage()}
                    className="w-10 h-10 rounded-full bg-[#38bdf8] hover:bg-[#0ea5e9] text-slate-950 flex items-center justify-center shadow-[0_0_15px_rgba(56,189,248,0.4)] shrink-0 transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                    title="Send prompt"
                  >
                    <Send size={15} className="translate-x-[1px]" />
                  </button>
                </div>
              </div>

              {/* Quick Prompt Suggestion Pills */}
              <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
                {quickPromptPills.map((pill, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(pill)}
                    className="px-4 py-1.5 rounded-full text-xs font-medium text-slate-300 bg-slate-900/60 hover:bg-slate-800/80 border border-white/10 hover:border-cyan-400/40 backdrop-blur-md shadow-xs transition-all cursor-pointer"
                  >
                    {pill}
                  </button>
                ))}
              </div>
            </div>

            {/* Bottom Footer with Tagline and Coordinates */}
            <div className="relative z-10 flex flex-col sm:flex-row items-center justify-between gap-2 mt-12 pb-2 text-[10px] sm:text-[10.5px] font-mono tracking-widest text-slate-400/80 max-w-5xl mx-auto w-full">
              <span>EXPLORE · ANALYZE · UNDERSTAND · BUILD A BETTER TOMORROW</span>
              <div className="flex items-center gap-1.5 text-slate-400 font-mono">
                <Crosshair size={13} className="text-cyan-400" />
                <span>28.6139° N  77.2090° E</span>
              </div>
            </div>
          </div>
        ) : (
          /* ========================================================== */
          /* 2. CHAT CONVERSATION STREAM VIEW (DARK MODE)               */
          /* ========================================================== */
          <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#070e18]">
            {/* Top Chat Bar with Back & Reset */}
            <div className="h-12 bg-[#0a1526] border-b border-cyan-500/20 px-4 flex items-center justify-between shrink-0 shadow-xs">
              <button
                onClick={handleStartNewAnalysis}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-300 hover:text-white transition-colors cursor-pointer"
              >
                <span>← Back to Overview</span>
              </button>

              <div className="flex items-center gap-2">
                {uploadedScenes.length > 0 && (
                  <span className="text-[11px] font-medium text-cyan-300 bg-cyan-950/60 px-2.5 py-1 rounded-lg border border-cyan-500/30">
                    {uploadedScenes.length} Image{uploadedScenes.length > 1 ? 's' : ''} Active
                  </span>
                )}
                <button
                  onClick={handleClearChat}
                  className="p-1.5 rounded-lg border border-slate-700 text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 transition-colors cursor-pointer"
                  title="Clear conversation"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>

            {/* Chat Stream Messages List */}
            <div className="flex-1 overflow-y-auto px-4 py-6 md:px-8 lg:px-12 space-y-6">
              <div className="max-w-4xl mx-auto space-y-6">
                {messages.map((msg, idx) => (
                  <div key={msg.id} className="animate-fadeUp">
                    {/* CASE 1: USER MESSAGE */}
                    {msg.role === 'user' ? (
                      <div className="flex items-start justify-end gap-3">
                        <div className="max-w-2xl space-y-2 text-right">
                          <div className="inline-block bg-gradient-to-r from-blue-950 to-slate-900 border border-cyan-500/30 text-white p-3.5 sm:p-4 rounded-2xl rounded-tr-xs text-xs sm:text-sm font-body shadow-lg text-left leading-relaxed">
                            <p>{msg.query}</p>

                            {/* Attached Scenes thumbnails in user message */}
                            {msg.scenesAttached && msg.scenesAttached.length > 0 && (
                              <div className="flex flex-wrap gap-2 mt-3 pt-2.5 border-t border-cyan-500/20">
                                {msg.scenesAttached.map((sc) => (
                                  <div
                                    key={sc.id}
                                    className="flex items-center gap-1.5 bg-black/40 border border-white/10 px-2 py-1 rounded-lg text-[11px] text-white/90"
                                  >
                                    {sc.preview && (
                                      <img
                                        src={sc.preview}
                                        alt={sc.name}
                                        className="w-4 h-4 rounded-xs object-cover"
                                      />
                                    )}
                                    <span className="truncate max-w-[120px] font-mono">{sc.name}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                          <p className="text-[10px] text-slate-500 font-mono pr-1">{msg.timestamp}</p>
                        </div>

                        <div className="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-400/50 text-cyan-200 flex items-center justify-center shrink-0 text-xs font-bold shadow-xs">
                          RM
                        </div>
                      </div>
                    ) : (
                      /* CASE 2: ASSISTANT (ORCHESTRATOR) RESPONSE */
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-cyan-500 text-slate-950 flex items-center justify-center shrink-0 shadow-[0_0_10px_rgba(56,189,248,0.4)]">
                          <Sparkles size={16} />
                        </div>

                        <div className="flex-1 max-w-3xl space-y-3">
                          {/* Assistant Message Bubble */}
                          <div className="bg-[#0b1626]/90 border border-cyan-500/25 rounded-2xl rounded-tl-xs p-4 sm:p-5 shadow-xl space-y-4 text-slate-200">
                            {/* Header: Detected Intent & Engaged Agent Badges */}
                            <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="font-bold text-xs sm:text-sm text-white font-display">
                                  {msg.intent || 'SatQuery Multi-Agent Analysis'}
                                </span>
                                {msg.agentsUsed &&
                                  msg.agentsUsed.map((agentName, aIdx) => (
                                    <span
                                      key={aIdx}
                                      className="inline-flex items-center gap-1 text-[10.5px] font-semibold px-2 py-0.5 rounded-full bg-slate-900 border border-cyan-500/30 text-cyan-300 font-mono"
                                    >
                                      {agentName}
                                    </span>
                                  ))}
                              </div>

                              {/* Confidence Badge */}
                              {msg.confidence && (
                                <span className="text-[10.5px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-300 border border-emerald-500/30">
                                  Conf: {msg.confidence}
                                </span>
                              )}
                            </div>

                            {/* Main Text Answer */}
                            <div className="text-xs sm:text-sm text-slate-200 leading-relaxed space-y-2 whitespace-pre-line font-body">
                              {msg.answer}
                            </div>

                            {/* Clarification Options if Query was Ambiguous */}
                            {msg.requiresClarification && msg.clarificationOptions && (
                              <div className="p-3 bg-amber-950/40 border border-amber-500/40 rounded-xl space-y-2">
                                <span className="text-xs font-bold text-amber-200 block">
                                  Did you mean one of the following?
                                </span>
                                <div className="flex flex-wrap gap-1.5">
                                  {msg.clarificationOptions.map((opt, i) => (
                                    <button
                                      key={i}
                                      onClick={() => handleSendMessage(opt)}
                                      className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 border border-amber-400/40 text-amber-200 hover:bg-amber-900/40 font-medium transition-colors cursor-pointer"
                                    >
                                      {opt}
                                    </button>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Interactive Change Intelligence Studio or Visual Evidence */}
                            {(() => {
                              const isChangeAnalysis = Boolean(
                                msg.changeData?.visualizations ||
                                msg.changeData?.regions ||
                                (msg.changeData?.categories && Object.keys(msg.changeData.categories).length > 0) ||
                                msg.intent?.toLowerCase().includes('change') ||
                                msg.agentsUsed?.some((a) => a.toLowerCase().includes('change')) ||
                                msg.imageEvidence?.some((ev) => ev.type?.includes('change'))
                              )

                              return (
                                <>
                                  {/* Render Interactive Studio when comparison/change is detected */}
                                  {isChangeAnalysis && (
                                    <div className="space-y-2 pt-2 border-t border-slate-800">
                                      <div className="flex items-center justify-between">
                                        <span className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider block font-sans">
                                          Interactive Visualization Studio
                                        </span>
                                        <span className="text-[10px] font-mono text-cyan-300/80 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
                                          Live Layer Switcher
                                        </span>
                                      </div>
                                      <ChangeIntelligenceStudio
                                        changeData={msg.changeData || {}}
                                        imageEvidence={msg.imageEvidence || []}
                                        attachedScenes={msg.attachedScenes || uploadedScenes || []}
                                      />
                                    </div>
                                  )}

                                  {/* Standard or Exported Layer Cards */}
                                  {msg.imageEvidence && msg.imageEvidence.length > 0 && (
                                    <div className="space-y-2 pt-2 border-t border-slate-800">
                                      <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block font-sans">
                                        {isChangeAnalysis ? 'Exported Image Layers' : 'Visual Evidence (Image Layers)'}
                                      </span>
                                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                        {msg.imageEvidence.map((ev, i) => (
                                          <div
                                            key={i}
                                            className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950 flex flex-col shadow-lg"
                                          >
                                            <div className="px-3 py-1.5 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between text-[10.5px] text-slate-300 font-mono">
                                              <span>{ev.title}</span>
                                              <span className="text-cyan-400">{ev.type}</span>
                                            </div>
                                            {ev.url_or_b64 ? (
                                              <div className="relative aspect-[16/10] bg-slate-900">
                                                <img
                                                  src={ev.url_or_b64}
                                                  alt={ev.title}
                                                  className="w-full h-full object-cover"
                                                />
                                              </div>
                                            ) : (
                                              <div className="p-3 text-slate-400 text-xs font-mono">
                                                Layer generated: {ev.file_path || 'Visual raster ready'}
                                              </div>
                                            )}
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </>
                              )
                            })()}

                            {/* Domain Knowledge Evidence (KNOWLEDGE_EVIDENCE) */}
                            {msg.knowledgeEvidence && msg.knowledgeEvidence.length > 0 && (
                              <div className="space-y-2 pt-2 border-t border-slate-800">
                                <span className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider block font-sans flex items-center gap-1.5">
                                  <FileText size={12} className="text-cyan-400" />
                                  <span>Domain Knowledge & Literature Evidence (RAG)</span>
                                </span>
                                <div className="space-y-2">
                                  {msg.knowledgeEvidence.map((k, i) => (
                                    <div
                                      key={i}
                                      className="p-3 bg-slate-900/60 border border-cyan-500/25 rounded-xl text-xs space-y-1"
                                    >
                                      <p className="font-semibold text-slate-100">{k.text}</p>
                                      <div className="flex items-center gap-2 text-[10.5px] text-cyan-400 font-mono">
                                        <span>Source: {k.source}</span>
                                        {k.section && <span>· Section: {k.section}</span>}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Execution Trace Dropdown Accordion */}
                            {msg.trace && (
                              <div className="pt-2 border-t border-slate-800">
                                <button
                                  type="button"
                                  onClick={() =>
                                    setExpandedTraceIndex(expandedTraceIndex === idx ? null : idx)
                                  }
                                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-cyan-300 font-mono transition-colors cursor-pointer"
                                >
                                  <Clock size={13} />
                                  <span>
                                    Execution Trace ({msg.trace.total_duration_seconds?.toFixed(3)}s)
                                  </span>
                                  {expandedTraceIndex === idx ? (
                                    <ChevronUp size={13} />
                                  ) : (
                                    <ChevronDown size={13} />
                                  )}
                                </button>

                                {expandedTraceIndex === idx && (
                                  <div className="mt-2.5 p-3 rounded-xl bg-slate-950 text-slate-300 text-xs font-mono space-y-2 border border-slate-800 animate-fadeIn">
                                    <div className="flex items-center justify-between text-slate-500 border-b border-slate-800 pb-1.5 text-[11px]">
                                      <span>Stage / Agent</span>
                                      <span>Duration</span>
                                    </div>
                                    {msg.trace.steps &&
                                      msg.trace.steps.map((step, sIdx) => (
                                        <div
                                          key={sIdx}
                                          className="flex items-start justify-between text-[11px] gap-2"
                                        >
                                          <div className="flex items-center gap-1.5 text-cyan-400 truncate">
                                            <CheckCircle2 size={11} className="shrink-0" />
                                            <span>{step.name}</span>
                                          </div>
                                          <span className="text-slate-400 shrink-0">
                                            {step.duration_seconds?.toFixed(3)}s
                                          </span>
                                        </div>
                                      ))}
                                    <div className="pt-1.5 border-t border-slate-800 text-[10px] text-slate-500">
                                      Selection reasoning: {msg.trace.selection_reasoning}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Actions bar: Copy & Download Report */}
                            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleCopy(msg.answer, idx)}
                                  className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-400 hover:text-white transition-colors p-1 rounded-md hover:bg-slate-800 cursor-pointer"
                                >
                                  {copiedIndex === idx ? (
                                    <>
                                      <Check size={12} className="text-cyan-400" />
                                      <span className="text-cyan-400">Copied</span>
                                    </>
                                  ) : (
                                    <>
                                      <Copy size={12} />
                                      <span>Copy</span>
                                    </>
                                  )}
                                </button>
                              </div>

                              {(msg.structuredForUi || msg.answer) && (
                                <DownloadReportButton
                                  reportData={
                                    msg.structuredForUi || {
                                      title: `SatQuery Analysis: ${msg.intent || 'Earth Observation'}`,
                                      analysisType: msg.intent || 'Change Detection Analysis',
                                      prediction: msg.answer,
                                      confidence: msg.confidence,
                                      agentsUsed: msg.agentsUsed,
                                      imageEvidence: msg.imageEvidence,
                                    }
                                  }
                                  analysisData={msg.structuredForUi}
                                  className="text-[11px] font-medium text-cyan-300 hover:text-white"
                                />
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {/* Loading indicator */}
                {loading && (
                  <div className="flex items-start gap-3 animate-fadeUp">
                    <div className="w-8 h-8 rounded-full bg-cyan-500 text-slate-950 flex items-center justify-center shrink-0">
                      <Sparkles size={16} className="animate-spin" />
                    </div>
                    <div className="p-4 rounded-2xl bg-slate-900 border border-cyan-500/30 shadow-lg flex items-center gap-3">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" />
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.2s]" />
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.4s]" />
                      </div>
                      <span className="text-xs font-mono text-cyan-300">
                        Orchestrating agents & reasoning over imagery...
                      </span>
                    </div>
                  </div>
                )}

                <div ref={chatBottomRef} />
              </div>
            </div>

            {/* Bottom Floating Prompt Box in Chat Mode */}
            <div className="p-4 bg-[#081322] border-t border-cyan-500/20 shrink-0">
              <div className="max-w-4xl mx-auto space-y-2">
                {/* Attached scene tags in prompt */}
                {uploadedScenes.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pb-1">
                    <span className="text-[10.5px] font-bold text-cyan-400 uppercase tracking-wider">
                      Attached ({uploadedScenes.length}):
                    </span>
                    {uploadedScenes.map((sc) => (
                      <div
                        key={sc.id}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-900 border border-cyan-500/30 text-cyan-200 text-xs"
                      >
                        {sc.preview && (
                          <img src={sc.preview} alt={sc.name} className="w-3.5 h-3.5 rounded-xs object-cover" />
                        )}
                        <span className="font-medium text-slate-200 text-[11px] max-w-[120px] truncate">
                          {sc.name}
                        </span>
                        <button
                          onClick={() => handleRemoveScene(sc.id)}
                          className="text-slate-400 hover:text-white"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="text-[11px] font-semibold text-cyan-400 hover:underline px-2 py-0.5 shrink-0"
                    >
                      + Add Image
                    </button>
                  </div>
                )}

                {/* Input Box Container */}
                <div className="relative rounded-2xl border border-cyan-500/35 focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-500/20 bg-slate-950/80 transition-all shadow-lg overflow-hidden">
                  <textarea
                    ref={textareaRef}
                    rows={1}
                    value={queryInput}
                    onChange={handleTextareaChange}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSendMessage()
                      }
                    }}
                    onPaste={handlePaste}
                    placeholder="Ask SatQuery AI anything about your imagery..."
                    className="w-full pl-4 pr-24 py-3.5 text-xs sm:text-sm text-white placeholder-slate-400 focus:outline-none resize-none font-body leading-relaxed max-h-40 bg-transparent"
                  />

                  {/* Right Action Icons in Input */}
                  <div className="absolute right-2.5 bottom-2.5 flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                      title="Attach satellite image"
                    >
                      <Paperclip size={16} />
                    </button>

                    <button
                      type="button"
                      disabled={!queryInput.trim() || loading}
                      onClick={() => handleSendMessage()}
                      className={`p-2 rounded-xl font-semibold transition-all shadow-sm ${
                        queryInput.trim() && !loading
                          ? 'bg-[#38bdf8] text-slate-950 hover:bg-[#0ea5e9] cursor-pointer'
                          : 'bg-slate-800 text-slate-600 cursor-not-allowed'
                      }`}
                      title="Send message"
                    >
                      <Send size={14} />
                    </button>
                  </div>
                </div>

                {/* Quick query suggestion chips */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[11px] text-slate-400">
                  <span className="font-semibold uppercase tracking-wider text-[10px] text-cyan-400">Try:</span>
                  {quickPromptPills.map((sug, sIdx) => (
                    <button
                      key={sIdx}
                      onClick={() => handleSendMessage(sug)}
                      className="px-2 py-0.5 rounded-md bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors cursor-pointer border border-white/5"
                    >
                      {sug}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
