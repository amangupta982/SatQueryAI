import { MapPin, CheckCircle, Crosshair, Sparkles, X } from 'lucide-react'

export default function RegionInspector({
  region,
  onClose,
  palette = {},
}) {
  if (!region) {
    return (
      <div className="bg-white p-4 rounded-xl border border-[#e5ebe7] shadow-sm flex flex-col items-center justify-center text-center text-[#7a9486] min-h-[220px]">
        <Crosshair size={32} className="stroke-1 mb-2 opacity-50" />
        <p className="text-xs font-medium">Click any detected change region on the map to inspect its physical and geographic properties.</p>
      </div>
    )
  }

  const catColor = palette[region.category] || '#ff4d4d'
  const hasGeo = region.geo && region.geo.latitude !== null && region.geo.longitude !== null

  return (
    <div className="bg-white p-4 rounded-xl border border-[#e5ebe7] shadow-sm flex flex-col gap-3 text-xs">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[#e5ebe7]">
        <div className="flex items-center gap-2">
          <span
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: catColor }}
          />
          <span className="font-bold text-sm text-[#162721]">{region.region_id}</span>
          <span className="bg-[#edf3f0] text-[#2d5243] text-[10px] px-2 py-0.5 rounded font-semibold uppercase tracking-wider">
            {region.category.replace('_', ' ')}
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-[#f2f6f4] rounded text-[#7a9486] hover:text-[#162721] transition"
        >
          <X size={15} />
        </button>
      </div>

      {/* Property Grid */}
      <div className="grid grid-cols-2 gap-2 text-[11px]">
        <div className="bg-[#f9faf9] p-2 rounded-lg border border-[#e5ebe7]">
          <span className="text-[#7a9486] block">Change Type</span>
          <span className="font-semibold text-[#162721] capitalize">{region.change_type}</span>
        </div>

        <div className="bg-[#f9faf9] p-2 rounded-lg border border-[#e5ebe7]">
          <span className="text-[#7a9486] block">Confidence</span>
          <span className="font-semibold text-[#162721]">{(region.confidence * 100).toFixed(1)}%</span>
        </div>

        <div className="bg-[#f9faf9] p-2 rounded-lg border border-[#e5ebe7]">
          <span className="text-[#7a9486] block">Area (Pixels)</span>
          <span className="font-semibold text-[#162721]">{region.area_pixels.toLocaleString()} px</span>
        </div>

        <div className="bg-[#f9faf9] p-2 rounded-lg border border-[#e5ebe7]">
          <span className="text-[#7a9486] block">Physical Area</span>
          <span className="font-semibold text-[#162721]">
            {region.area_m2 ? `${region.area_m2.toLocaleString()} m²` : 'Pixel units only'}
          </span>
        </div>
      </div>

      {/* Spatial Localization */}
      <div className="bg-[#f4f7f5] p-2.5 rounded-lg border border-[#dce7e1] flex flex-col gap-1.5">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-[#2d5243]">
          <MapPin size={13} />
          <span>Spatial & Geospatial Coordinates</span>
        </div>

        <div className="text-[11px] text-[#4d665a] flex flex-col gap-1">
          <div>
            <span className="font-medium">Image Centroid: </span>
            <span>[{region.centroid_pixel[0]}, {region.centroid_pixel[1]}]</span>
          </div>
          <div>
            <span className="font-medium">Bounding Box: </span>
            <span>[{region.bbox.join(', ')}]</span>
          </div>

          {hasGeo ? (
            <div className="pt-1 mt-1 border-t border-[#dce7e1] text-[#234238]">
              <div><span className="font-medium">Latitude: </span>{region.geo.latitude.toFixed(6)}°</div>
              <div><span className="font-medium">Longitude: </span>{region.geo.longitude.toFixed(6)}°</div>
              {region.geo.crs && <div><span className="font-medium">CRS: </span>{region.geo.crs}</div>}
            </div>
          ) : (
            <div className="text-[10px] text-[#7a9486] italic pt-1 border-t border-[#dce7e1]">
              Geospatial projection not attached to input raster. Pixel coordinates are exact.
            </div>
          )}
        </div>
      </div>

      {/* Semantic Transition Evidence */}
      {(region.t1_dominant_class || region.t2_dominant_class) && (
        <div className="flex items-center justify-between text-[11px] bg-[#edf3f0] p-2 rounded-lg border border-[#dce7e1]">
          <span className="text-[#5c7569]">Temporal Shift:</span>
          <span className="font-semibold text-[#162721]">
            {region.t1_dominant_class || 'Unknown'} → {region.t2_dominant_class || region.category}
          </span>
        </div>
      )}
    </div>
  )
}
