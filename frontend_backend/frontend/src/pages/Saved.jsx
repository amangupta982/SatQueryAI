import Header from '../components/Header'
import { historyItems } from '../data/mockData'
import { BookmarkCheck, MapPin } from 'lucide-react'

const saved = historyItems.slice(0, 3)

export default function Saved({ onOpenMobileNav }) {
  return (
    <div className="flex flex-col h-full min-h-0">
      <Header title="Saved Analyses" status={`${saved.length} bookmarked`} onOpenMobileNav={onOpenMobileNav} />
      <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-3 max-w-2xl">
        {saved.map((item) => (
          <div key={item.id} className="glass rounded-xl p-3.5 flex items-center gap-3.5">
            <img src={item.thumbnail} alt={item.filename} className="w-14 h-14 rounded-lg object-cover shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-200 truncate">{item.filename}</p>
              <div className="flex items-center gap-1 text-[11px] text-slate-500 mt-1">
                <MapPin size={11} /> {item.location}
              </div>
            </div>
            <BookmarkCheck size={16} className="text-cyan-accent shrink-0" />
          </div>
        ))}
      </div>
    </div>
  )
}
