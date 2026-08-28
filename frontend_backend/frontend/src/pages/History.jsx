import { useNavigate } from 'react-router-dom'
import { historyItems } from '../data/mockData'
import { MapPin, Boxes, ChevronRight } from 'lucide-react'

export default function History() {
  const navigate = useNavigate()

  return (
    <div className="flex-1 overflow-y-auto p-4 lg:p-6 bg-[#f8f9fb]">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {historyItems.map((item) => (
          <button
            key={item.id}
            onClick={() => navigate('/')}
            className="glass rounded-xl overflow-hidden text-left group bg-white hover:border-sky-300 border border-slate-200 transition-all shadow-sm"
          >
            <div className="h-32 overflow-hidden bg-slate-100">
              <img
                src={item.thumbnail}
                alt={item.filename}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>
            <div className="p-3.5">
              <div className="flex items-start justify-between gap-2">
                <p className="text-[13px] font-medium text-slate-800 truncate">{item.filename}</p>
                <ChevronRight size={14} className="text-slate-400 group-hover:text-cyan-soft shrink-0 mt-0.5" />
              </div>
              <p className="text-[11px] text-slate-500 font-mono mt-1">{item.date}</p>
              <div className="flex items-center gap-1 text-[11px] text-slate-500 mt-1.5">
                <MapPin size={11} />
                {item.location}
              </div>
              <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-100">
                <div className="flex items-center gap-1 text-[11px] text-slate-600">
                  <Boxes size={12} />
                  {item.objects} objects
                </div>
                <span
                  className={`text-[10.5px] px-2 py-0.5 rounded-full border font-medium ${
                    item.status === 'Completed'
                      ? 'text-emerald-700 border-emerald-300 bg-emerald-50'
                      : 'text-amber-700 border-amber-300 bg-amber-50'
                  }`}
                >
                  {item.status}
                </span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
