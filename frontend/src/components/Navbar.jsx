import React from 'react'
import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand">
        <div>
          <div className="navbar-logo">⚡ Texas Venom</div>
          <div className="navbar-subtitle">NCS Dashboard</div>
        </div>
      </NavLink>
      <ul className="navbar-nav">
        <li><NavLink to="/" end>Teams</NavLink></li>
        <li><NavLink to="/search">Search</NavLink></li>
        <li><NavLink to="/agent">AI Agent</NavLink></li>
      </ul>
    </nav>
  )
}
