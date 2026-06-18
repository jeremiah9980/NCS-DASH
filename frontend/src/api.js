import axios from 'axios'

// In dev, Vite proxies /api to localhost:8000 (see vite.config.js).
// In production (GitHub Pages), there is no proxy, so the deployed backend
// URL must be supplied at build time via VITE_API_URL.
const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL })

export const getTeams = (params) => api.get('/teams', { params }).then(r => r.data)
export const getTeam = (id) => api.get(`/teams/${id}`).then(r => r.data)
export const getRoster = (id) => api.get(`/teams/${id}/roster`).then(r => r.data)
export const getHistory = (id, limit = 50) => api.get(`/teams/${id}/history`, { params: { limit } }).then(r => r.data)
export const searchTeams = (params) => api.get('/search/teams', { params }).then(r => r.data)
export const searchPlayers = (params) => api.get('/search/players', { params }).then(r => r.data)
export const agentQuery = (body) => api.post('/agent/query', body).then(r => r.data)
