import { useEffect, useRef, useState } from 'react'
import { Mic, Paperclip, SendHorizontal, Satellite } from 'lucide-react'
import ChatMessage from './ChatMessage'
import SuggestedQueries from './SuggestedQueries'
import { initialChatMessages, getMockAIResponse } from '../data/mockData'

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function ChatPanel({ onLayerSuggestion, className = '' }) {
  const [messages, setMessages] = useState(initialChatMessages)
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, typing])

  const sendMessage = (text) => {
    const value = text ?? input
    if (!value.trim()) return

    const userMsg = { id: crypto.randomUUID(), role: 'user', text: value, time: now() }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setTyping(true)

    setTimeout(() => {
      const res = getMockAIResponse(value)
      const aiMsg = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: res.text,
        stats: res.stats,
        highlight: res.highlight,
        time: now(),
      }
      setMessages((m) => [...m, aiMsg])
      setTyping(false)
      if (res.activateLayer) onLayerSuggestion?.(res.activateLayer)
    }, 1100)
  }

  return (
    <div className={`flex flex-col h-full bg-base-900/60 ${className}`}>
      <div className="h-16 shrink-0 flex items-center gap-2.5 px-4 border-b border-white/[0.06]">
        <div className="w-8 h-8 rounded-lg bg-cyan-accent/10 border border-cyan-accent/25 flex items-center justify-center">
          <Satellite size={15} className="text-cyan-accent" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-100 flex items-center gap-1.5">
            SatQuery AI
            <span className="flex items-center gap-1 text-[10.5px] font-normal text-signal-lime">
              <span className="w-1.5 h-1.5 rounded-full bg-signal-lime animate-pulseSlow" /> Online
            </span>
          </p>
          <p className="text-[11px] text-slate-500 truncate">Ask questions about your satellite image</p>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
        {typing && (
          <div className="flex gap-2 animate-fadeUp">
            <div className="w-6 h-6 rounded-full bg-cyan-accent/15 border border-cyan-accent/25 flex items-center justify-center shrink-0">
              <Satellite size={11} className="text-cyan-accent" />
            </div>
            <div className="bg-white/[0.035] border border-white/[0.07] rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" />
            </div>
          </div>
        )}
      </div>

      <SuggestedQueries onSelect={(q) => setInput(q)} />

      <div className="px-3 pb-3 pt-1 border-t border-white/[0.06] shrink-0">
        <div className="flex items-center gap-1.5 rounded-xl border border-white/[0.09] bg-white/[0.02] px-2 py-1.5 focus-within:border-cyan-accent/40">
          <button className="w-7 h-7 flex items-center justify-center text-slate-500 hover:text-slate-200 shrink-0">
            <Paperclip size={15} />
          </button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask anything about this satellite image..."
            className="flex-1 min-w-0 bg-transparent text-[13px] text-slate-200 placeholder:text-slate-600 outline-none"
          />
          <button className="w-7 h-7 flex items-center justify-center text-slate-500 hover:text-slate-200 shrink-0">
            <Mic size={15} />
          </button>
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim()}
            className="w-7 h-7 flex items-center justify-center rounded-lg bg-cyan-accent text-base-950 disabled:opacity-30 disabled:bg-slate-600 shrink-0 hover:bg-cyan-soft transition-colors"
          >
            <SendHorizontal size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}
