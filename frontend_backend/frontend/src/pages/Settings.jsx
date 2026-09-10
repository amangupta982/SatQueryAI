import { useState } from 'react'
import Header from '../components/Header'
import { userProfile } from '../data/mockData'

function Toggle({ enabled, onChange }) {
  return (
    <button
      onClick={() => onChange(!enabled)}
      className={`w-9 h-5 rounded-full relative transition-colors shrink-0 ${enabled ? 'bg-[#234238]' : 'bg-slate-200'}`}
    >
      <span
        className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${
          enabled ? 'translate-x-4' : 'translate-x-0.5'
        }`}
      />
    </button>
  )
}

export default function Settings() {
  const [darkMode, setDarkMode] = useState(false)
  const [notifications, setNotifications] = useState(true)
  const [autoDetect, setAutoDetect] = useState(true)
  const [highRes, setHighRes] = useState(false)

  return (
    <div className="flex-1 overflow-y-auto p-4 lg:p-6 max-w-xl space-y-5 bg-[#fafaf8] text-[#162721] selection:bg-[#dce7e1] selection:text-[#162721]">
        <div className="glass rounded-xl p-4 flex items-center gap-3.5 bg-white border border-[#e5ebe7] shadow-sm">
          <div className="w-12 h-12 rounded-full bg-[#e2eae5] border border-[#c8d4ce] flex items-center justify-center text-sm font-semibold text-[#234238]">
            {userProfile.avatarInitials}
          </div>
          <div>
            <p className="text-sm font-medium text-slate-800">{userProfile.name}</p>
            <p className="text-[11px] text-slate-500">{userProfile.team}</p>
          </div>
        </div>

        <div className="glass rounded-xl divide-y divide-slate-100 bg-white border border-[#e5ebe7] shadow-sm">
          <Row label="Dark interface" desc="Use the dark navy AI workspace theme" value={darkMode} onChange={setDarkMode} />
          <Row label="Notifications" desc="Alerts when an analysis finishes processing" value={notifications} onChange={setNotifications} />
          <Row label="Auto-run detection" desc="Automatically enable AI Detection layer after analysis" value={autoDetect} onChange={setAutoDetect} />
          <Row label="High-resolution preview" desc="Load full-resolution imagery in the viewer" value={highRes} onChange={setHighRes} />
        </div>
      </div>
  )
}

function Row({ label, desc, value, onChange }) {
  return (
    <div className="flex items-center justify-between gap-4 p-4">
      <div>
        <p className="text-sm font-medium text-slate-800">{label}</p>
        <p className="text-[11px] text-slate-500 mt-0.5">{desc}</p>
      </div>
      <Toggle enabled={value} onChange={onChange} />
    </div>
  )
}
