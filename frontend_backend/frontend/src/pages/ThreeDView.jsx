import { useState, useEffect } from 'react'

/**
 * ThreeDView — embeds the existing 3D View application (running on port 4173)
 * inside an iframe, displaying seamlessly beneath the SatQueryAI header.
 */
const THREED_VIEW_URL =
  import.meta.env.VITE_3D_VIEW_URL ||
  (typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:4173`
    : 'http://localhost:4173')

export default function ThreeDView() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    let unmounted = false
    fetch(THREED_VIEW_URL, { mode: 'no-cors' })
      .then(() => {
        if (!unmounted) setError(false)
      })
      .catch(() => {
        if (!unmounted) {
          setError(true)
          setLoading(false)
        }
      })
    return () => {
      unmounted = true
    }
  }, [])

  return (
    <div className="flex-1 relative w-full h-full overflow-hidden bg-[#0a0a0a]">
      {/* Loading state */}
      {loading && !error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-[#0a0a0a]">
          <div className="w-10 h-10 border-2 border-[#234238] border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-[#8a9a92] text-sm font-medium">Loading 3D View…</p>
        </div>
      )}

      {/* Error state — 3D server not running */}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-[#0a0a0a]">
          <div className="text-center max-w-md px-6">
            <div className="w-12 h-12 rounded-full bg-[#1a2420] flex items-center justify-center mx-auto mb-4">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6b7c73" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <h2 className="text-[#c8d4cc] text-lg font-semibold mb-2">3D View Server Not Running</h2>
            <p className="text-[#6b7c73] text-sm mb-4">
              The 3D View application needs to be running separately.
            </p>
            <code className="block bg-[#111] text-[#8a9a92] text-xs p-3 rounded-lg font-mono text-left">
              cd 3d-view<br />
              npm run dev
            </code>
          </div>
        </div>
      )}

      {/* Iframe embedding the existing 3D View application */}
      <iframe
        src={THREED_VIEW_URL}
        title="3D View"
        className="w-full h-full border-0"
        style={{ display: error ? 'none' : 'block' }}
        onLoad={() => setLoading(false)}
        onError={() => {
          setLoading(false)
          setError(true)
        }}
        allow="accelerometer; gyroscope; fullscreen; autoplay; clipboard-write"
      />
    </div>
  )
}
