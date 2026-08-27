import { NavLink } from 'react-router-dom'
import {
  Satellite,
  LayoutDashboard,
  ScanSearch,
  History,
  BookmarkCheck,
  Database,
  Upload,
  Layers,
  Boxes,
  Sprout,
  GitCompare,
  Settings,
  HelpCircle,
  ChevronsLeft,
  ChevronsRight,
} from 'lucide-react'
import { userProfile } from '../data/mockData'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/new-analysis', label: 'New Analysis', icon: ScanSearch },
  { to: '/history', label: 'Image History', icon: History },
  { to: '/saved', label: 'Saved Analyses', icon: BookmarkCheck },
  { to: '/datasets', label: 'Datasets', icon: Database },
]

const toolItems = [
  { to: '/new-analysis?tool=upload', label: 'Image Upload', icon: Upload },
  { to: '/compare', label: 'Compare Images', icon: GitCompare },
  { to: '/detection', label: 'Object Detection', icon: Boxes },
  { to: '/land-cover', label: 'Land Cover Analysis', icon: Sprout },
  { to: '/change-detection', label: 'Change Detection', icon: Layers },
]

function NavItem({ to, label, icon: Icon, end, collapsed }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
          isActive
            ? 'bg-cyan-accent/10 text-cyan-soft shadow-glow border border-cyan-accent/20'
            : 'text-slate-400 hover:text-slate-100 hover:bg-white/[0.04] border border-transparent'
        }`
      }
      title={collapsed ? label : undefined}
    >
      <Icon size={17} strokeWidth={1.8} className="shrink-0" />
      {!collapsed && <span className="truncate">{label}</span>}
    </NavLink>
  )
}

export default function Sidebar({ collapsed, onToggle, mobileOpen, onCloseMobile }) {
  return (
    <>
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={onCloseMobile}
        />
      )}
      <aside
        className={`fixed lg:static z-50 h-full flex flex-col shrink-0 bg-base-900/95 border-r border-white/[0.06] transition-all duration-200
          ${collapsed ? 'lg:w-[76px]' : 'lg:w-[248px]'}
          ${mobileOpen ? 'translate-x-0 w-[248px]' : '-translate-x-full lg:translate-x-0 w-[248px]'}
        `}
      >
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-4 h-16 border-b border-white/[0.06] shrink-0">
          <div className="flex items-center justify-center w-8 h-8 rounded-md bg-cyan-accent/10 border border-cyan-accent/30 shrink-0">
            <Satellite size={16} className="text-cyan-accent" strokeWidth={2} />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="font-display font-semibold text-[15px] text-slate-100 leading-tight truncate">SatQuery AI</p>
              <p className="text-[10.5px] text-slate-500 leading-tight truncate">Vision-Language Remote Sensing</p>
            </div>
          )}
          <button
            onClick={onToggle}
            className="hidden lg:flex ml-auto items-center justify-center w-6 h-6 rounded text-slate-500 hover:text-slate-200 hover:bg-white/[0.06]"
          >
            {collapsed ? <ChevronsRight size={14} /> : <ChevronsLeft size={14} />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          <div className="space-y-1">
            {!collapsed && <p className="px-3 pb-1.5 text-[10.5px] font-semibold tracking-wider text-slate-600 uppercase">Navigate</p>}
            {navItems.map((item) => (
              <NavItem key={item.label} {...item} collapsed={collapsed} />
            ))}
          </div>
          <div className="space-y-1">
            {!collapsed && <p className="px-3 pb-1.5 text-[10.5px] font-semibold tracking-wider text-slate-600 uppercase">Tools</p>}
            {toolItems.map((item) => (
              <NavItem key={item.label} {...item} collapsed={collapsed} />
            ))}
          </div>
        </nav>

        <div className="border-t border-white/[0.06] px-3 py-3 space-y-1 shrink-0">
          <NavItem to="/settings" label="Settings" icon={Settings} collapsed={collapsed} />
          <NavItem to="/help" label="Help" icon={HelpCircle} collapsed={collapsed} />
          <div className={`flex items-center gap-2.5 rounded-lg px-3 py-2 mt-1 ${collapsed ? 'justify-center' : ''}`}>
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-cyan-accent/40 to-base-600 border border-cyan-accent/30 flex items-center justify-center text-[11px] font-semibold text-cyan-soft shrink-0">
              {userProfile.avatarInitials}
            </div>
            {!collapsed && (
              <div className="min-w-0">
                <p className="text-xs font-medium text-slate-200 truncate">{userProfile.name}</p>
                <p className="text-[10.5px] text-slate-500 truncate">{userProfile.role}</p>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  )
}
