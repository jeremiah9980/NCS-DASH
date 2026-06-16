import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getTeams } from '../api'

export default function Home() {
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [division, setDivision] = useState('')
  const [city, setCity] = useState('')

  const load = () => {
    setLoading(true)
    getTeams({ division: division || undefined, city: city || undefined })
      .then(setTeams)
      .catch(() => setError('Failed to load teams'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  return (
    <div>
      <div className="page-header">
        <h1>Central Texas Teams</h1>
        <p>Browse NCS fastpitch teams for 10U and 12U divisions.</p>
      </div>

      <div className="form-row mb-2">
        <div className="form-group">
          <label>Division</label>
          <select value={division} onChange={e => setDivision(e.target.value)}>
            <option value="">All Divisions</option>
            <option value="10U">10U</option>
            <option value="12U">12U</option>
          </select>
        </div>
        <div className="form-group">
          <label>City</label>
          <input
            placeholder="e.g. Austin"
            value={city}
            onChange={e => setCity(e.target.value)}
          />
        </div>
        <button className="btn" onClick={load}>Filter</button>
      </div>

      {loading && <p className="loading">Loading teams…</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && teams.length === 0 && (
        <p className="text-muted">No teams found. Configure NCS_SEED_EVENT_IDS and run the scraper to populate data.</p>
      )}

      <div className="team-grid">
        {teams.map(team => (
          <Link key={team.id} to={`/teams/${team.id}`} className="team-card">
            <div className="team-card-inner">
              <div className="team-name">{team.name}</div>
              <div className="team-meta">
                <span className="badge">{team.division}</span>
                {team.city && <span className="badge">{team.city}</span>}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
