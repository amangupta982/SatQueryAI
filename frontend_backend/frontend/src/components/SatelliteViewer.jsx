import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import {
  Plus,
  Minus,
  Maximize2,
  Minimize2,
  RotateCcw,
  Layers as LayersIcon,
  ChevronDown,
} from 'lucide-react'
import LayerControls from './LayerControls'

const INITIAL_CENTER = [13.0827, 77.5946]
const INITIAL_ZOOM = 16

// Simulated geo-referenced AI detection overlays for the active satellite area
const BUILDING_BOXES = [
  { bounds: [[13.0842, 77.5925], [13.0849, 77.5934]], label: 'Commercial Complex', confidence: 96 },
  { bounds: [[13.0835, 77.5918], [13.0841, 77.5927]], label: 'Residential Block A', confidence: 94 },
  { bounds: [[13.0828, 77.5912], [13.0834, 77.5921]], label: 'Residential Block B', confidence: 92 },
  { bounds: [[13.0819, 77.5908], [13.0826, 77.5916]], label: 'Warehouse Structure', confidence: 95 },
  { bounds: [[13.0852, 77.5940], [13.0858, 77.5948]], label: 'Urban Building', confidence: 91 },
  { bounds: [[13.0812, 77.5922], [13.0818, 77.5931]], label: 'Riverfront Facility', confidence: 93 },
  { bounds: [[13.0805, 77.5930], [13.0811, 77.5938]], label: 'Building Structure', confidence: 89 },
]

const ROAD_LINES = [
  {
    latlngs: [
      [13.0865, 77.5895],
      [13.0845, 77.5920],
      [13.0827, 77.5946],
      [13.0810, 77.5975],
      [13.0795, 77.6000],
    ],
    label: 'Primary Arterial Highway (Bridge)',
  },
  {
    latlngs: [
      [13.0850, 77.5905],
      [13.0832, 77.5922],
      [13.0818, 77.5940],
    ],
    label: 'Connecting Urban Road',
  },
]

const WATER_POLYGON = [
  [13.0875, 77.5932],
  [13.0850, 77.5938],
  [13.0830, 77.5945],
  [13.0815, 77.5955],
  [13.0790, 77.5970],
  [13.0785, 77.5985],
  [13.0800, 77.5980],
  [13.0825, 77.5965],
  [13.0845, 77.5955],
  [13.0870, 77.5948],
]

const VEGETATION_POLYGONS = [
  [
    [13.0870, 77.5955],
    [13.0855, 77.5965],
    [13.0830, 77.5980],
    [13.0810, 77.6005],
    [13.0850, 77.6015],
    [13.0875, 77.5995],
  ],
  [
    [13.0830, 77.5900],
    [13.0815, 77.5910],
    [13.0805, 77.5900],
    [13.0820, 77.5890],
  ],
]

export default function SatelliteViewer({ layers = ['satellite', 'detection'], onToggleLayer }) {
  const mapContainerRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const overlayLayersRef = useRef({})
  const [showLayers, setShowLayers] = useState(false)
  const [fullscreen, setFullscreen] = useState(false)
  const [coordinates, setCoordinates] = useState('13.0827° N, 77.5946° E')
  const [zoomLevel, setZoomLevel] = useState(INITIAL_ZOOM)

  // Initialize Leaflet Interactive Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return

    // Create Leaflet map instance with disabled default zoom buttons so custom UI controls it
    const map = L.map(mapContainerRef.current, {
      center: INITIAL_CENTER,
      zoom: INITIAL_ZOOM,
      zoomControl: false,
      attributionControl: false,
      maxZoom: 19,
      minZoom: 3,
    })

    // High-resolution Esri World Imagery Satellite Tiles
    const satelliteTileLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {
        maxZoom: 19,
        subdomains: ['server', 'services'],
      }
    )
    satelliteTileLayer.addTo(map)

    // Layer groups for AI detection overlays
    const buildingsGroup = L.layerGroup()
    const roadsGroup = L.layerGroup()
    const waterGroup = L.layerGroup()
    const vegetationGroup = L.layerGroup()

    // 1. Draw Buildings (Emerald Polygons/Rectangles)
    BUILDING_BOXES.forEach((b) => {
      const rect = L.rectangle(b.bounds, {
        color: '#10b981',
        weight: 2,
        fillColor: '#10b981',
        fillOpacity: 0.25,
      })
      rect.bindTooltip(
        `<div class="text-xs font-semibold text-slate-800 p-0.5">🏢 ${b.label} <span class="text-emerald-600">(${b.confidence}%)</span></div>`,
        { sticky: true, opacity: 0.95 }
      )
      rect.addTo(buildingsGroup)
    })

    // 2. Draw Roads (Amber Polylines)
    ROAD_LINES.forEach((r) => {
      const polyline = L.polyline(r.latlngs, {
        color: '#f59e0b',
        weight: 4,
        dashArray: '6, 6',
        opacity: 0.9,
      })
      polyline.bindTooltip(
        `<div class="text-xs font-semibold text-slate-800 p-0.5">🛣️ ${r.label}</div>`,
        { sticky: true, opacity: 0.95 }
      )
      polyline.addTo(roadsGroup)
    })

    // 3. Draw Water Bodies (Sky Blue Polygon)
    const waterPoly = L.polygon(WATER_POLYGON, {
      color: '#0284c7',
      weight: 2,
      fillColor: '#0284c7',
      fillOpacity: 0.35,
    })
    waterPoly.bindTooltip(
      '<div class="text-xs font-semibold text-slate-800 p-0.5">💧 River / Water Body (~80m avg dist)</div>',
      { sticky: true, opacity: 0.95 }
    )
    waterPoly.addTo(waterGroup)

    // 4. Draw Vegetation (Green Canopy Polygons)
    VEGETATION_POLYGONS.forEach((poly) => {
      const vegPoly = L.polygon(poly, {
        color: '#22c55e',
        weight: 2,
        fillColor: '#22c55e',
        fillOpacity: 0.3,
      })
      vegPoly.bindTooltip(
        '<div class="text-xs font-semibold text-slate-800 p-0.5">🌳 Canopy Vegetation Cluster</div>',
        { sticky: true, opacity: 0.95 }
      )
      vegPoly.addTo(vegetationGroup)
    })

    overlayLayersRef.current = {
      buildings: buildingsGroup,
      roads: roadsGroup,
      water: waterGroup,
      vegetation: vegetationGroup,
    }

    // Update coordinates and zoom on move
    const updateCoords = () => {
      const center = map.getCenter()
      const lat = center.lat.toFixed(4)
      const lng = center.lng.toFixed(4)
      const latDir = center.lat >= 0 ? 'N' : 'S'
      const lngDir = center.lng >= 0 ? 'E' : 'W'
      setCoordinates(`${Math.abs(lat)}° ${latDir}, ${Math.abs(lng)}° ${lngDir}`)
      setZoomLevel(map.getZoom())
    }

    map.on('move', updateCoords)
    map.on('zoomend', updateCoords)

    mapInstanceRef.current = map

    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [])

  // Sync active layers with Leaflet map
  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map) return

    const overlays = overlayLayersRef.current
    const isDetectionActive = layers.includes('detection')

    // Buildings
    if (overlays.buildings) {
      if (layers.includes('buildings') || isDetectionActive) {
        if (!map.hasLayer(overlays.buildings)) map.addLayer(overlays.buildings)
      } else {
        if (map.hasLayer(overlays.buildings)) map.removeLayer(overlays.buildings)
      }
    }

    // Roads
    if (overlays.roads) {
      if (layers.includes('roads') || isDetectionActive) {
        if (!map.hasLayer(overlays.roads)) map.addLayer(overlays.roads)
      } else {
        if (map.hasLayer(overlays.roads)) map.removeLayer(overlays.roads)
      }
    }

    // Water
    if (overlays.water) {
      if (layers.includes('water') || isDetectionActive) {
        if (!map.hasLayer(overlays.water)) map.addLayer(overlays.water)
      } else {
        if (map.hasLayer(overlays.water)) map.removeLayer(overlays.water)
      }
    }

    // Vegetation
    if (overlays.vegetation) {
      if (layers.includes('vegetation') || isDetectionActive) {
        if (!map.hasLayer(overlays.vegetation)) map.addLayer(overlays.vegetation)
      } else {
        if (map.hasLayer(overlays.vegetation)) map.removeLayer(overlays.vegetation)
      }
    }
  }, [layers])

  // Invalidate map size when fullscreen toggles
  useEffect(() => {
    setTimeout(() => {
      mapInstanceRef.current?.invalidateSize()
    }, 200)
  }, [fullscreen])

  const handleZoomIn = () => mapInstanceRef.current?.zoomIn()
  const handleZoomOut = () => mapInstanceRef.current?.zoomOut()
  const handleReset = () => {
    mapInstanceRef.current?.setView(INITIAL_CENTER, INITIAL_ZOOM, { animate: true })
  }

  // Calculate dynamic scale representation
  const scaleMeters = Math.max(10, Math.round(100 * Math.pow(2, 16 - zoomLevel)))

  return (
    <div
      className={`relative rounded-2xl overflow-hidden border border-slate-200 bg-slate-900 shadow-xs select-none ${
        fullscreen ? 'fixed inset-3 z-50 shadow-2xl' : 'w-full h-full'
      }`}
    >
      {/* Interactive Leaflet Map Container */}
      <div ref={mapContainerRef} className="absolute inset-0 w-full h-full z-0 cursor-grab active:cursor-grabbing" />

      {/* Top-left Vertical Control Box matching screenshot */}
      <div className="absolute top-4 left-4 flex flex-col bg-white/95 backdrop-blur-sm border border-slate-200 rounded-xl shadow-md divide-y divide-slate-100 z-10">
        <button
          onClick={handleZoomIn}
          title="Zoom in (+)"
          className="p-2.5 text-slate-700 hover:text-slate-900 hover:bg-slate-50 transition-colors rounded-t-xl"
        >
          <Plus size={15} strokeWidth={2.2} />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom out (-)"
          className="p-2.5 text-slate-700 hover:text-slate-900 hover:bg-slate-50 transition-colors"
        >
          <Minus size={15} strokeWidth={2.2} />
        </button>
        <button
          onClick={() => setFullscreen((v) => !v)}
          title={fullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          className="p-2.5 text-slate-700 hover:text-slate-900 hover:bg-slate-50 transition-colors"
        >
          {fullscreen ? <Minimize2 size={14} strokeWidth={2} /> : <Maximize2 size={14} strokeWidth={2} />}
        </button>
        <button
          onClick={handleReset}
          title="Reset to Center"
          className="p-2.5 text-slate-700 hover:text-slate-900 hover:bg-slate-50 transition-colors rounded-b-xl"
        >
          <RotateCcw size={14} strokeWidth={2} />
        </button>
      </div>

      {/* Top-right Layers button matching screenshot */}
      <div className="absolute top-4 right-4 z-10">
        <button
          onClick={() => setShowLayers((v) => !v)}
          className="flex items-center gap-2 bg-white/95 backdrop-blur-sm border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-semibold text-slate-800 hover:bg-slate-50 shadow-md transition-colors"
        >
          <LayersIcon size={14} className="text-slate-700" strokeWidth={2} />
          <span>Layers</span>
          <ChevronDown size={13} className="text-slate-400" />
        </button>

        {showLayers && (
          <div className="absolute top-11 right-0 mt-1 z-20">
            <LayerControls layers={layers} onToggle={onToggleLayer} />
          </div>
        )}
      </div>

      {/* Bottom-left Scale Pill */}
      <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm border border-slate-200 rounded-xl px-3 py-1.5 text-xs font-mono text-slate-700 shadow-md flex items-center gap-2 z-10">
        <div className="w-6 h-[2px] bg-slate-700 inline-block border-l-2 border-r-2 border-slate-700" />
        <span className="font-semibold text-slate-800">{scaleMeters >= 1000 ? `${(scaleMeters / 1000).toFixed(1)} km` : `${scaleMeters} m`}</span>
      </div>

      {/* Bottom-right Coordinates Pill (Real-time Live Updating) */}
      <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-sm border border-slate-200 rounded-xl px-3.5 py-1.5 text-xs font-mono text-slate-800 font-semibold shadow-md z-10">
        <span>{coordinates}</span>
      </div>
    </div>
  )
}
