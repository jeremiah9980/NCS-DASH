import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import TeamDetail from './pages/TeamDetail'
import Search from './pages/Search'
import AgentChat from './pages/AgentChat'

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/teams/:id" element={<TeamDetail />} />
          <Route path="/search" element={<Search />} />
          <Route path="/agent" element={<AgentChat />} />
        </Routes>
      </main>
      <footer className="footer">
        <p>© {new Date().getFullYear()} Texas Venom — NCS Central Texas Dashboard</p>
      </footer>
    </div>
  )
}
