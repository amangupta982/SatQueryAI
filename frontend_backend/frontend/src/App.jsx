import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import NewAnalysis from './pages/NewAnalysis'
import History from './pages/History'
import Detection from './pages/Detection'
import LandCover from './pages/LandCover'
import Settings from './pages/Settings'
import Help from './pages/Help'

export default function App() {
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#f8f9fb] text-slate-800 font-body">
      {/* Top Header full-width with complete navigation */}
      <Header />

      <main className="flex-1 min-w-0 h-full overflow-hidden flex flex-col">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new-analysis" element={<NewAnalysis />} />
          <Route path="/history" element={<History />} />
          <Route path="/detection" element={<Detection />} />
          <Route path="/land-cover" element={<LandCover />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
        </Routes>
      </main>
    </div>
  )
}
