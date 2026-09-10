import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  Home,
  BarChart2,
  History as HistoryIcon,
  Database,
  HelpCircle,
  Plus,
  Bell,
  Menu,
  X,
} from 'lucide-react'

const navLinks = [
  { to: '/', label: 'Overview', icon: Home, end: true },
  { to: '/new-analysis', label: 'Analyses', icon: BarChart2 },
  { to: '/history', label: 'History', icon: HistoryIcon },
  { to: '/datasets', label: 'Datasets', icon: Database },
  { to: '/help', label: 'Help', icon: HelpCircle },
]

export default function Header() {
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

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
          {navLinks.map((link) => (
            <NavLink
              key={link.label}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `text-[13.5px] font-medium transition-all py-1 ${
                  isActive
                    ? 'text-[#162721] font-bold border-b-2 border-[#234238]'
                    : 'text-[#5d6f66] hover:text-[#162721]'
                }`
              }
            >
              <span>{link.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3.5">
          {/* AI Engine Status */}
          <div className="hidden md:flex items-center gap-2 text-xs font-medium text-[#2d4239]">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.7)]" />
            <span>AI Engine Online</span>
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
          {navLinks.map((link) => (
            <NavLink
              key={link.label}
              to={link.to}
              end={link.end}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-[#e5ede8] text-[#234238]'
                    : 'text-[#5d6f66] hover:bg-[#f2f6f3]'
                }`
              }
            >
              <span>{link.label}</span>
            </NavLink>
          ))}
        </div>
      )}
    </header>
  )
}
