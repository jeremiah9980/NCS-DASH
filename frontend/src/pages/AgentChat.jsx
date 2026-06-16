import React, { useState, useRef, useEffect } from 'react'
import { agentQuery } from '../api'

const SUGGESTIONS = [
  { label: 'All 10U teams', query: { division: '10U' } },
  { label: 'Austin 12U teams', query: { division: '12U', city: 'Austin' } },
  { label: 'Find player "Smith"', query: { player: 'Smith' } },
  { label: 'CenTex Force changes', query: { team: 'CenTex Force' } },
]

function parseInput(text) {
  const q = {}
  const teamMatch = text.match(/team[:\s]+([a-z0-9 ]+)/i)
  const playerMatch = text.match(/player[:\s]+([a-z0-9 ]+)/i)
  const divMatch = text.match(/\b(10U|12U|14U|16U|18U)\b/i)
  const cityMatch = text.match(/\b(austin|cedar park|round rock|georgetown|pflugerville|leander|kyle|buda)\b/i)
  if (teamMatch) q.team = teamMatch[1].trim()
  if (playerMatch) q.player = playerMatch[1].trim()
  if (divMatch) q.division = divMatch[1].toUpperCase()
  if (cityMatch) q.city = cityMatch[1]
  return q
}

function formatResult(data) {
  if (!data.count) return 'No changes found matching your query.'
  const lines = [`Found ${data.count} change(s):\n`]
  data.results.slice(0, 10).forEach(r => {
    const icon = r.change_type === 'added' ? '🟢' : '🔴'
    lines.push(`${icon} ${r.player} — ${r.team} (${r.division}) — ${r.change_type} on ${new Date(r.change_time).toLocaleDateString()}`)
  })
  if (data.count > 10) lines.push(`\n…and ${data.count - 10} more.`)
  return lines.join('\n')
}

export default function AgentChat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hi! I can help you query NCS roster changes. Try asking about a team, player, division, or city — or click a suggestion below.',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (text, query) => {
    if (!text.trim()) return
    setMessages(prev => [...prev, { role: 'user', text }])
    setLoading(true)
    setInput('')
    try {
      const q = query || parseInput(text)
      const data = await agentQuery(q)
      setMessages(prev => [...prev, { role: 'assistant', text: formatResult(data) }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Sorry, something went wrong reaching the API.' }])
    } finally {
      setLoading(false)
    }
  }

  const onKeyDown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) } }

  return (
    <div>
      <div className="page-header">
        <h1>AI Agent</h1>
        <p>Ask about rosters, changes, players, teams, or divisions using natural language.</p>
      </div>

      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>{m.text}</div>
        ))}
        {loading && <div className="chat-bubble assistant loading">Thinking…</div>}
        <div ref={bottomRef} />
      </div>

      <div className="form-row mb-2" style={{ flexWrap: 'wrap', gap: '0.5rem' }}>
        {SUGGESTIONS.map(s => (
          <button key={s.label} className="btn btn-outline text-sm" style={{ padding: '0.4rem 0.9rem' }}
            onClick={() => send(s.label, s.query)}>
            {s.label}
          </button>
        ))}
      </div>

      <div className="chat-input-row">
        <input
          placeholder='e.g. "Show me all 10U Austin teams" or "player: Smith"'
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={loading}
        />
        <button className="btn" onClick={() => send(input)} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  )
}
