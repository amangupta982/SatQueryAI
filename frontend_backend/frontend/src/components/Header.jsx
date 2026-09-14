import { useState, useEffect, useRef } from 'react'
import { NavLink, useNavigate, useLocation } from 'react-router-dom'
import {
  Plus,
  Bell,
  Menu,
  X,
  ChevronDown,
  BarChart2,
  MessageSquare,
  Ruler,
  GitCompareArrows,
  Radio,
  BookOpen,
} from 'lucide-react'

const analysisItems = [
  { to: '/new-analysis', label: 'Analyses', icon: BarChart2 },
  { to: '/vqa', label: 'Ask VQA', icon: MessageSquare },
  { to: '/area-measurement', label: 'Area', icon: Ruler },
  { to: '/change-analysis', label: 'Change Intelligence', icon: GitCompareArrows },
  { to: '/optical-sar', label: 'Optical-SAR', icon: Radio },
  { to: '/new-analysis#rag-knowledge', label: 'RAG Knowledge', icon: BookOpen },
]

export default function Header() {
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [mobileAnalysesOpen, setMobileAnalysesOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)
  const closeTimeoutRef = useRef(null)
  const [modelStatus, setModelStatus] = useState({ status: 'checking', label: 'Checking SatQuery-VQA...' })

  // Active check for any analysis page
  const isAnalysisActive = analysisItems.some((item) => {
    if (item.to === '/new-analysis') {
      return location.pathname === '/new-analysis' || location.pathname.startsWith('/analyses')
    }
    return (
      location.pathname === item.to ||
      (item.to === '/change-analysis' && location.pathname === '/change-intelligence')
    )
  })

  // Debounced hover handlers to eliminate flickering and gaps
  const handleMouseEnter = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
      closeTimeoutRef.current = null
    }
    setDropdownOpen(true)
  }

  const handleMouseLeave = () => {
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
    }
    closeTimeoutRef.current = setTimeout(() => {
      setDropdownOpen(false)
    }, 180)
  }

  const handleToggleClick = (e) => {
    e.stopPropagation()
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
      closeTimeoutRef.current = null
    }
    setDropdownOpen((prev) => !prev)
  }

  // Close dropdown on outside click or Escape key
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
      }
    }
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current)
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  useEffect(() => {
    let unmounted = false
    const check = async () => {
      try {
        const res = await fetch('/api/v1/vqa/status')
        if (res.ok) {
          const data = await res.json()
          if (!unmounted) {
            if (data.is_loaded) {
              setModelStatus({ status: 'loaded', label: 'SatQuery-VQA Loaded' })
            } else if (data.status === 'loading') {
              setModelStatus({ status: 'loading', label: 'Loading SatQuery-VQA' })
            } else {
              setModelStatus({ status: 'unavailable', label: 'Model Unavailable' })
            }
          }
        } else {
          if (!unmounted) setModelStatus({ status: 'unavailable', label: 'Model Unavailable' })
        }
      } catch {
        if (!unmounted) setModelStatus({ status: 'unavailable', label: 'Model Unavailable' })
      }
    }
    check()
    const interval = setInterval(check, 6000)
    return () => {
      unmounted = true
      clearInterval(interval)
    }
  }, [])

  return (
    <header className="h-[68px] shrink-0 bg-[#fafaf8] border-b border-[#e5ebe7] sticky top-0 z-40 select-none">
      <div className="h-full px-4 lg:px-8 flex items-center justify-between gap-4">
        {/* Left: Brand Identity */}
        <div
          className="flex items-center gap-3 cursor-pointer group shrink-0"
          onClick={() => navigate('/')}
        >
          {/* Earth/clover logo in Forest Green */}
          <div className="text-[#234238] flex items-center justify-center">
            <svg
              width="26"
              height="26"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-[#234238]"
            >
              <path d="M12 2a4 4 0 0 0-4 4c0 2.5 4 6 4 6s4-3.5 4-6a4 4 0 0 0-4-4Z" />
              <path d="M12 22a4 4 0 0 0 4-4c0-2.5-4-6-4-6s-4 3.5-4 6a4 4 0 0 0 4 4Z" />
              <path d="M2 12a4 4 0 0 0 4 4c2.5 0 6-4 6-4s-3.5-4-6-4a4 4 0 0 0-4 4Z" />
              <path d="M22 12a4 4 0 0 0-4-4c-2.5 0-6 4-6 4s3.5 4 6 4a4 4 0 0 0 4 4Z" />
            </svg>
          </div>
          <div>
            <span className="font-display font-bold text-[#162721] text-[15px] tracking-tight leading-none block">
              SatQuery AI
            </span>
            <p className="text-[11px] text-[#6b7c73] font-normal leading-tight mt-0.5">
              Satellite Intelligence for Earth Observation
            </p>
          </div>
        </div>

        {/* Center Navigation Links (Desktop - Centered clean text links) */}
        <nav className="hidden lg:flex items-center gap-8 absolute left-1/2 -translate-x-1/2 z-10">
          {/* Overview */}
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `text-[13.5px] font-medium transition-all py-1 ${
                isActive
                  ? 'text-[#162721] font-bold border-b-2 border-[#234238]'
                  : 'text-[#5d6f66] hover:text-[#162721]'
              }`
            }
          >
            <span>Overview</span>
          </NavLink>

          {/* Analyses Dropdown */}
          <div
            ref={dropdownRef}
            className="relative py-2"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
          >
            <button
              type="button"
              onClick={handleToggleClick}
              className={`text-[13.5px] font-medium transition-all py-1 px-2 rounded-lg flex items-center gap-1.5 cursor-pointer select-none ${
                isAnalysisActive
                  ? 'text-[#162721] font-bold border-b-2 border-[#234238]'
                  : dropdownOpen
                  ? 'text-[#162721] bg-[#edf3f0]'
                  : 'text-[#5d6f66] hover:text-[#162721] hover:bg-[#f2f6f4]'
              }`}
              aria-haspopup="true"
              aria-expanded={dropdownOpen}
            >
              <span>Analyses</span>
              <ChevronDown
                size={14}
                className={`transition-transform duration-200 ${
                  dropdownOpen ? 'rotate-180 text-[#234238]' : 'text-[#7a8c83]'
                }`}
              />
            </button>

            {dropdownOpen && (
              <div
                className="absolute top-full left-1/2 -translate-x-1/2 pt-1.5 -mt-1 w-56 z-50 animate-fadeIn"
                role="menu"
              >
                <div className="bg-[#fafaf8] border border-[#dce7e1] rounded-2xl shadow-xl p-1.5 space-y-0.5">
                  {analysisItems.map((item) => {
                    const isItemActive = item.to.includes('#')
                      ? location.pathname + location.hash === item.to
                      : item.to === '/new-analysis'
                      ? (location.pathname === '/new-analysis' && !location.hash) || location.pathname.startsWith('/analyses')
                      : location.pathname === item.to ||
                        (item.to === '/change-analysis' && location.pathname === '/change-intelligence')
                    const Icon = item.icon
                    return (
                      <NavLink
                        key={item.to}
                        to={item.to}
                        onClick={() => setDropdownOpen(false)}
                        role="menuitem"
                        className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] transition-colors ${
                          isItemActive
                            ? 'bg-[#e5ede8] text-[#234238] font-bold'
                            : 'text-[#5d6f66] hover:text-[#162721] hover:bg-[#f2f6f3]'
                        }`}
                      >
                        {Icon && (
                          <Icon
                            size={15}
                            className={`shrink-0 ${isItemActive ? 'text-[#234238]' : 'text-[#7a8c83]'}`}
                          />
                        )}
                        <span className="flex-1">{item.label}</span>
                        {isItemActive && (
                          <span className="w-1.5 h-1.5 rounded-full bg-[#234238] shrink-0" />
                        )}
                      </NavLink>
                    )
                  })}
                </div>
              </div>
            )}
          </div>

          {/* History */}
          <NavLink
            to="/history"
            className={({ isActive }) =>
              `text-[13.5px] font-medium transition-all py-1 ${
                isActive
                  ? 'text-[#162721] font-bold border-b-2 border-[#234238]'
                  : 'text-[#5d6f66] hover:text-[#162721]'
              }`
            }
          >
            <span>History</span>
          </NavLink>

          {/* Datasets */}
          <NavLink
            to="/datasets"
            className={({ isActive }) =>
              `text-[13.5px] font-medium transition-all py-1 ${
                isActive
                  ? 'text-[#162721] font-bold border-b-2 border-[#234238]'
                  : 'text-[#5d6f66] hover:text-[#162721]'
              }`
            }
          >
            <span>Datasets</span>
          </NavLink>

          {/* 3D View */}
          <NavLink
            to="/3d-view"
            className={({ isActive }) =>
              `text-[13.5px] font-medium transition-all py-1 ${
                isActive
                  ? 'text-[#162721] font-bold border-b-2 border-[#234238]'
                  : 'text-[#5d6f66] hover:text-[#162721]'
              }`
            }
          >
            <span>3D View</span>
          </NavLink>
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3.5">
          {/* AI Model Status */}
          <div className="hidden md:flex items-center gap-2 text-xs font-medium text-[#2d4239]">
            <span
              className={`w-2 h-2 rounded-full ${
                modelStatus.status === 'loaded'
                  ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.7)]'
                  : modelStatus.status === 'loading'
                  ? 'bg-amber-500 animate-pulse'
                  : 'bg-rose-500'
              }`}
            />
            <span className="font-mono text-[11px] font-semibold">{modelStatus.label}</span>
          </div>

          {/* + New Analysis Button in Deep Forest Green */}
          <button
            onClick={() => navigate('/new-analysis')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#234238] hover:bg-[#1b342c] text-white text-xs font-semibold shadow-sm transition-all cursor-pointer"
          >
            <Plus size={14} strokeWidth={2.5} />
            <span>New Analysis</span>
          </button>

          {/* Notification Bell */}
          <button
            title="Notifications"
            className="hidden sm:flex w-9 h-9 rounded-full bg-white border border-[#d8e0dc] hover:border-[#b8c6c0] text-[#5d6f66] hover:text-[#162721] items-center justify-center transition-colors shadow-2xs"
          >
            <Bell size={15} strokeWidth={1.8} />
          </button>

          {/* AS User Avatar in Deep Forest Green */}
          <div className="w-9 h-9 rounded-full bg-[#234238] text-white flex items-center justify-center text-xs font-bold shrink-0 shadow-2xs">
            AS
          </div>

          {/* Mobile menu toggle */}
          <button
            onClick={() => setMobileMenuOpen((v) => !v)}
            className="lg:hidden p-2 rounded-xl text-[#5d6f66] hover:text-[#162721] hover:bg-[#edf2ef]"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Top Navigation Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-[#fafaf8] border-b border-[#e5ebe7] px-4 py-3 space-y-1 shadow-lg animate-fadeUp">
          <NavLink
            to="/"
            end
            onClick={() => setMobileMenuOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-[#e5ede8] text-[#234238]'
                  : 'text-[#5d6f66] hover:bg-[#f2f6f3]'
              }`
            }
          >
            <span>Overview</span>
          </NavLink>

          {/* Mobile Analyses Group */}
          <div className="pt-0.5 pb-0.5">
            <button
              type="button"
              onClick={() => setMobileAnalysesOpen((v) => !v)}
              className={`w-full flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isAnalysisActive
                  ? 'bg-[#e5ede8] text-[#234238]'
                  : 'text-[#5d6f66] hover:bg-[#f2f6f3]'
              }`}
            >
              <span>Analyses</span>
              <ChevronDown
                size={14}
                className={`transition-transform duration-150 ${
                  mobileAnalysesOpen ? 'rotate-180 text-[#234238]' : 'text-[#7a8c83]'
                }`}
              />
            </button>
            {mobileAnalysesOpen && (
              <div className="pl-3 mt-1 space-y-1 border-l-2 border-[#dce7e1] ml-3">
                {analysisItems.map((item) => {
                  const isItemActive = item.to.includes('#')
                    ? location.pathname + location.hash === item.to
                    : item.to === '/new-analysis'
                    ? (location.pathname === '/new-analysis' && !location.hash) || location.pathname.startsWith('/analyses')
                    : location.pathname === item.to ||
                      (item.to === '/change-analysis' && location.pathname === '/change-intelligence')
                  const Icon = item.icon
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      onClick={() => {
                        setMobileMenuOpen(false)
                        setMobileAnalysesOpen(false)
                      }}
                      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                        isItemActive
                          ? 'bg-[#e5ede8] text-[#234238] font-semibold'
                          : 'text-[#5d6f66] hover:bg-[#f2f6f3]'
                      }`}
                    >
                      {Icon && <Icon size={14} className={isItemActive ? 'text-[#234238]' : 'text-[#7a8c83]'} />}
                      <span>{item.label}</span>
                    </NavLink>
                  )
                })}
              </div>
            )}
          </div>

          <NavLink
            to="/history"
            onClick={() => setMobileMenuOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-[#e5ede8] text-[#234238]'
                  : 'text-[#5d6f66] hover:bg-[#f2f6f3]'
              }`
            }
          >
            <span>History</span>
          </NavLink>

          <NavLink
            to="/datasets"
            onClick={() => setMobileMenuOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-[#e5ede8] text-[#234238]'
                  : 'text-[#5d6f66] hover:bg-[#f2f6f3]'
              }`
            }
          >
            <span>Datasets</span>
          </NavLink>

          <NavLink
            to="/3d-view"
            onClick={() => setMobileMenuOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-[#e5ede8] text-[#234238]'
                  : 'text-[#5d6f66] hover:bg-[#f2f6f3]'
              }`
            }
          >
            <span>3D View</span>
          </NavLink>
        </div>
      )}
    </header>
  )
}
