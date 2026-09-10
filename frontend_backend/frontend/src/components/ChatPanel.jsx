import { useEffect, useRef, useState } from 'react'
import { Send, Sparkles, Paperclip } from 'lucide-react'
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

    const userMsg = { id: crypto.randomUUID(), role: 'user', text: value, time: now(), delivered: true }
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
    }, 1000)
  }

  return (
    <div className={`flex flex-col h-full bg-white rounded-2xl border border-slate-200 shadow-xs ${className}`}>
      {/* Header matching screenshot */}
      <div className="h-16 shrink-0 flex items-center justify-between px-4 border-b border-slate-150">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
            <Sparkles size={16} />
          </div>
          <div>
            <h2 className="text-xs font-bold text-slate-900 leading-tight">SatQuery AI</h2>
            <p className="text-[10.5px] text-slate-400 leading-tight">Your Satellite Copilot</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-xs font-medium text-slate-700">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Online</span>
        </div>
      </div>

      {/* Message List */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3.5">
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
        {typing && (
          <div className="flex gap-2.5 animate-fadeUp">
            <div className="w-6 h-6 rounded-full bg-blue-100 border border-blue-200 flex items-center justify-center shrink-0 mt-0.5 text-blue-600">
              <Sparkles size={13} />
            </div>
            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-3 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" />
            </div>
          </div>
        )}
      </div>

      {/* Suggested Queries */}
      <SuggestedQueries onSelect={(q) => sendMessage(q)} />

      {/* Input Box & Disclaimer */}
      <div className="p-3 border-t border-slate-150">
        <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50/80 px-2.5 py-1.5 focus-within:border-[#234238] focus-within:bg-white focus-within:ring-2 focus-within:ring-[#234238]/15 transition-all">
          <button
            type="button"
            title="Attach file"
            className="p-1 text-slate-400 hover:text-slate-600 transition-colors shrink-0"
          >
            <Paperclip size={15} />
          </button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask anything about this image..."
            className="flex-1 min-w-0 bg-transparent text-xs text-slate-800 placeholder:text-slate-400 outline-none"
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim()}
            className="w-8 h-8 flex items-center justify-center rounded-xl bg-[#234238] text-white disabled:opacity-40 hover:bg-[#1a342c] transition-colors shrink-0 shadow-xs"
          >
            <Send size={13} />
          </button>
        </div>
        <p className="text-[10px] text-slate-400 text-center mt-2">AI responses may not be 100% accurate.</p>
      </div>
    </div>
  )
}
