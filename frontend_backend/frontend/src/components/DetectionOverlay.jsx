import { detectionBoxes, detectionLegend } from '../data/mockData'

const colorFor = (type) => detectionLegend.find((l) => l.type === type)?.color || '#3fd4d0'

export default function DetectionOverlay({ activeTypes }) {
  const visible = detectionBoxes.filter((b) => activeTypes.includes(b.type))
  if (visible.length === 0) return null

  return (
    <div className="absolute inset-0 pointer-events-none">
      {visible.map((box) => {
        const color = colorFor(box.type)
        return (
          <div
            key={box.id}
            className="absolute animate-fadeUp"
            style={{
              left: `${box.x}%`,
              top: `${box.y}%`,
              width: `${box.w}%`,
              height: `${box.h}%`,
              border: `1.5px solid ${color}`,
              boxShadow: `0 0 10px -2px ${color}`,
              borderRadius: 3,
            }}
          >
            <span
              className="absolute -top-5 left-0 whitespace-nowrap text-[9.5px] font-mono font-medium px-1.5 py-[1px] rounded"
              style={{ background: `${color}CC`, color: '#050a12' }}
            >
              {box.label} {box.confidence}%
            </span>
          </div>
        )
      })}
    </div>
  )
}
