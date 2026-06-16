import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { searchTeams, searchPlayers } from '../api'

export default function Search() {
  const [mode, setMode] = useState('teams')
  const [query, setQuery] = useState('')
  const [division, setDivision] = useState('')
  const [city, setCity] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSearch = (e) => {
    e.preventDefault()
    setLoading(true)
    const fn = mode === 'teams' ? searchTeams : searchPlayers
    const params = { q: query || undefined }
    if (mode === 'teams') {
      if (division) params.division = division
      if (city) params.city = city
    }
    fn(params)
      .then(setResults)
      .finally(() => setLoading(false))
  }

  return (
    <div>
      <div className="page-header">
        <h1>Search</h1>
        <p>Find teams or players across Central Texas NCS rosters.</p>
      </div>

      <div className="tabs">
        <button className={`tab-btn ${mode === 'teams' ? 'active' : ''}`} onClick={() => { setMode('teams'); setResults(null) }}>Teams</button>
        <button className={`tab-btn ${mode === 'players' ? 'active' : ''}`} onClick={() => { setMode('players'); setResults(null) }}>Players</button>
      </div>

      <form onSubmit={handleSearch}>
        <div className="form-row">
          <div className="form-group">
            <label>{mode === 'teams' ? 'Team Name' : 'Player Name'}</label>
            <input
              placeholder={mode === 'teams' ? 'e.g. CenTex Force' : 'e.g. Smith'}
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          {mode === 'teams' && (
            <>
              <div className="form-group">
                <label>Division</label>
                <select value={division} onChange={e => setDivision(e.target.value)}>
                  <option value="">All</option>
                  <option value="10U">10U</option>
                  <option value="12U">12U</option>
                </select>
              </div>
              <div className="form-group">
                <label>City</label>
                <input placeholder="e.g. Austin" value={city} onChange={e => setCity(e.target.value)} />
              </div>
            </>
          )}
          <button type="submit" className="btn">{loading ? 'Searching…' : 'Search'}</button>
        </div>
      </form>

      {results !== null && (
        results.length === 0
          ? <p className="text-muted">No results found.</p>
          : mode === 'teams'
            ? (
              <div className="team-grid">
                {results.map(t => (
                  <Link key={t.id} to={`/teams/${t.id}`} className="team-card">
                    <div className="team-card-inner">
                      <div className="team-name">{t.name}</div>
                      <div className="team-meta">
                        <span className="badge">{t.division}</span>
                        {t.city && <span className="badge">{t.city}</span>}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )
            : (
              <table className="data-table">
                <thead><tr><th>Player</th><th>#</th><th>Status</th><th>Team</th></tr></thead>
                <tbody>
                  {results.map(p => (
                    <tr key={p.id}>
                      <td>{p.name}</td>
                      <td className="text-muted">{p.number || '—'}</td>
                      <td><span className={`badge ${p.status === 'active' ? 'badge-green' : 'badge-red'}`}>{p.status}</span></td>
                      <td><Link to={`/teams/${p.team_id}`} className="text-gold">View Team</Link></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
      )}
    </div>
  )
}
