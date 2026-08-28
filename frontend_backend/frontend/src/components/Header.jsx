import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  Home,
  BarChart2,
  History as HistoryIcon,
  Box,
  Sprout,
  Plus,
  Bell,
  Menu,
  X,
} from 'lucide-react'

const navLinks = [
  { to: '/', label: 'Overview', icon: Home, end: true },
  { to: '/new-analysis', label: 'Analyses', icon: BarChart2 },
  { to: '/history', label: 'History', icon: HistoryIcon },
  { to: '/detection', label: 'Object Detection', icon: Box },
  { to: '/land-cover', label: 'Land Cover', icon: Sprout },
]

export default function Header() {
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="h-[68px] shrink-0 bg-[#050c1a] border-b border-slate-800/80 sticky top-0 z-40 select-none">
      <div className="h-full px-4 lg:px-6 flex items-center justify-between gap-3">
        {/* Left: Brand Identity */}
        <div
          className="flex items-center gap-3 cursor-pointer group shrink-0"
          onClick={() => navigate('/')}
        >
          {/* Blue clover logo */}
          <div className="text-blue-500 flex items-center justify-center">
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-[#2b6cee]"
            >
              <path d="M12 2a4 4 0 0 0-4 4c0 2.5 4 6 4 6s4-3.5 4-6a4 4 0 0 0-4-4Z" />
              <path d="M12 22a4 4 0 0 0 4-4c0-2.5-4-6-4-6s-4 3.5-4 6a4 4 0 0 0 4 4Z" />
              <path d="M2 12a4 4 0 0 0 4 4c2.5 0 6-4 6-4s-3.5-4-6-4a4 4 0 0 0-4 4Z" />
              <path d="M22 12a4 4 0 0 0-4-4c-2.5 0-6 4-6 4s3.5 4 6 4a4 4 0 0 0 4 4Z" />
            </svg>
          </div>
          <div>
            <span className="font-display font-bold text-white text-base tracking-tight leading-none block">
              SatQuery AI
            </span>
            <p className="text-[11px] text-slate-400 font-normal leading-tight mt-0.5">
              Satellite Intelligence
            </p>
          </div>
        </div>

        {/* Center Navigation Pill Bar (Desktop - Mathematically Centered) */}
        <nav className="hidden xl:flex items-center absolute left-1/2 -translate-x-1/2 bg-[#0c1836] border border-blue-950/80 p-1 rounded-full gap-1 z-10 shadow-md shadow-black/20">
          {navLinks.map((link) => (
            <NavLink
              key={link.label}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all duration-150 ${
                  isActive
                    ? 'bg-[#1d61f2] text-white shadow-sm'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/40'
                }`
              }
            >
              <link.icon size={14} strokeWidth={2} />
              <span>{link.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3.5">
          {/* AI Engine Status */}
          <div className="hidden md:flex items-center gap-2 text-xs font-medium text-slate-200">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <span>AI Engine Online</span>
          </div>

          {/* + New Analysis Button */}
          <button
            onClick={() => navigate('/new-analysis')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#1d61f2] hover:bg-blue-600 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition-colors"
          >
            <Plus size={14} strokeWidth={2.5} />
            <span>New Analysis</span>
          </button>

          {/* Notification Bell */}
          <button
            title="Notifications"
            className="hidden sm:flex w-9 h-9 rounded-full bg-[#0a152e] border border-slate-800 text-slate-300 hover:text-white items-center justify-center transition-colors"
          >
            <Bell size={15} strokeWidth={1.8} />
          </button>

          {/* AS User Avatar */}
          <div className="w-9 h-9 rounded-full bg-[#1e4db7] border border-blue-400/30 text-white flex items-center justify-center text-xs font-bold shrink-0">
            AS
          </div>

          {/* Mobile menu toggle */}
          <button
            onClick={() => setMobileMenuOpen((v) => !v)}
            className="xl:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Top Navigation Dropdown */}
      {mobileMenuOpen && (
        <div className="xl:hidden bg-[#071126] border-b border-slate-800 px-4 py-3 space-y-1 shadow-2xl animate-fadeUp">
          {navLinks.map((link) => (
            <NavLink
              key={link.label}
              to={link.to}
              end={link.end}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-[#1d61f2] text-white'
                    : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                }`
              }
            >
              <link.icon size={16} strokeWidth={1.8} />
              <span>{link.label}</span>
            </NavLink>
          ))}
        </div>
      )}
    </header>
  )
}
