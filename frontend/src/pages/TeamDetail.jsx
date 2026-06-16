import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getTeam, getRoster, getHistory } from '../api'

export default function TeamDetail() {
  const { id } = useParams()
  const [team, setTeam] = useState(null)
  const [roster, setRoster] = useState([])
  const [history, setHistory] = useState([])
  const [tab, setTab] = useState('roster')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([getTeam(id), getRoster(id), getHistory(id)])
      .then(([t, r, h]) => { setTeam(t); setRoster(r); setHistory(h) })
      .catch(() => setError('Failed to load team data'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="loading">Loading…</p>
  if (error) return <p className="error">{error}</p>
  if (!team) return null

  return (
    <div>
      <Link to="/" className="text-gold text-sm">← All Teams</Link>
      <div className="page-header mt-2">
        <h1>{team.name}</h1>
        <div className="team-meta mt-1">
          <span className="badge">{team.division}</span>
          {team.city && <span className="badge">{team.city}</span>}
          {team.region && <span className="badge">{team.region}</span>}
        </div>
      </div>

      <div className="tabs">
        <button className={`tab-btn ${tab === 'roster' ? 'active' : ''}`} onClick={() => setTab('roster')}>
          Roster ({roster.length})
        </button>
        <button className={`tab-btn ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}>
          Change History ({history.length})
        </button>
      </div>

      {tab === 'roster' && (
        roster.length === 0
          ? <p className="text-muted">No active players on record.</p>
          : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player Name</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {roster.map(p => (
                  <tr key={p.id}>
                    <td className="text-muted">{p.number || '—'}</td>
                    <td>{p.name}</td>
                    <td><span className="badge badge-green">{p.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
      )}

      {tab === 'history' && (
        history.length === 0
          ? <p className="text-muted">No changes recorded yet.</p>
          : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date / Time</th>
                  <th>Player</th>
                  <th>Change</th>
                </tr>
              </thead>
              <tbody>
                {history.map(c => (
                  <tr key={c.id}>
                    <td className="text-sm text-muted">{new Date(c.change_time).toLocaleString()}</td>
                    <td>{c.player_name}</td>
                    <td>
                      <span className={`badge ${c.change_type === 'added' ? 'badge-green' : 'badge-red'}`}>
                        {c.change_type}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
      )}
    </div>
  )
}
