import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import homeIcon from '../assets/icons/home.svg'
import bookIcon from '../assets/icons/book.svg'
import detectIcon from '../assets/icons/detect.svg'
import contactIcon from '../assets/icons/contact.svg'

export default function NavBar() {
  const [open, setOpen] = useState(false)

  return (
    <nav className={open ? 'open' : ''}>
      <div className="logo">
        <span className="mark">AI</span>
        <span className="name">DETECTOR</span>
      </div>

      <button
        className={`hamburger ${open ? 'is-active' : ''}`}
        aria-label="Toggle menu"
        onClick={() => setOpen(!open)}
      >
        <span />
        <span />
        <span />
      </button>

      <ul className={`nav-links ${open ? 'show' : ''}`}>
        <li>
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : undefined)}>
            <img src={homeIcon} alt="home" height="20" />
            <span>Home</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/learn" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            <img src={bookIcon} alt="learn" height="20" />
            <span>Learn</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/content-detect" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            <img src={detectIcon} alt="content-detect" height="22" />
            <span>Content Detect</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/contact" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            <img src={contactIcon} alt="contact" height="22" />
            <span>Contact</span>
          </NavLink>
        </li>
      </ul>

      <div className="right-nav">
        <NavLink to="/sign-in" id="sign-in-btn">Sign In</NavLink>
        <button id="try-now-btn">Try Now</button>
      </div>
    </nav>
  )
}