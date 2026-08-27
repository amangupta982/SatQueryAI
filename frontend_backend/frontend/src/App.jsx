import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import NewAnalysis from './pages/NewAnalysis'
import History from './pages/History'
import Saved from './pages/Saved'
import Datasets from './pages/Datasets'
import Compare from './pages/Compare'
import Detection from './pages/Detection'
import LandCover from './pages/LandCover'
import ChangeDetection from './pages/ChangeDetection'
import Settings from './pages/Settings'
import Help from './pages/Help'

export default function App() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const openMobileNav = () => setMobileOpen(true)
  const closeMobileNav = () => setMobileOpen(false)

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-base-950">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((v) => !v)}
        mobileOpen={mobileOpen}
        onCloseMobile={closeMobileNav}
      />
      <main className="flex-1 min-w-0 h-full overflow-hidden">
        <Routes>
          <Route path="/" element={<Dashboard onOpenMobileNav={openMobileNav} />} />
          <Route path="/new-analysis" element={<NewAnalysis onOpenMobileNav={openMobileNav} />} />
          <Route path="/history" element={<History onOpenMobileNav={openMobileNav} />} />
          <Route path="/saved" element={<Saved onOpenMobileNav={openMobileNav} />} />
          <Route path="/datasets" element={<Datasets onOpenMobileNav={openMobileNav} />} />
          <Route path="/compare" element={<Compare onOpenMobileNav={openMobileNav} />} />
          <Route path="/detection" element={<Detection onOpenMobileNav={openMobileNav} />} />
          <Route path="/land-cover" element={<LandCover onOpenMobileNav={openMobileNav} />} />
          <Route path="/change-detection" element={<ChangeDetection onOpenMobileNav={openMobileNav} />} />
          <Route path="/settings" element={<Settings onOpenMobileNav={openMobileNav} />} />
          <Route path="/help" element={<Help onOpenMobileNav={openMobileNav} />} />
        </Routes>
      </main>
    </div>
  )
}
