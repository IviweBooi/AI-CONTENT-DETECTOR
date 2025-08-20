import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import homeIcon from '../assets/icons/home.svg'
import bookIcon from '../assets/icons/book.svg'
import detectIcon from '../assets/icons/detect.svg'
import helpIcon from '../assets/icons/help.svg'
import signinIcon from '../assets/icons/signin.svg'

export default function NavBar() {
  const [open, setOpen] = useState(false)

  return (
    <nav className={open ? 'open' : ''}>
      <div className="logo">
        <span className="mark">ZE</span>
        <span className="name">DETECTOR</span>
      </div>

      <div className="mobile-actions">
        <button
          className={`hamburger ${open ? 'is-active' : ''}`}
          aria-label="Toggle menu"
          onClick={() => setOpen(!open)}
        >
          <span />
          <span />
          <span />
        </button>
      </div>

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
            <img src={detectIcon} alt="detect" height="20" />
            <span>Detector</span>
          </NavLink>
        </li>
        <li>
          <NavLink to="/help" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            <img src={helpIcon} alt="help" height="20" />
            <span>Help</span>
          </NavLink>
        </li>
        {/* Mobile-only Sign In link inside menu */}
        <li className="mobile-only">
          <NavLink to="/sign-in" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            <img src={signinIcon} alt="sign in" height="20" />
            <span>Sign In</span>
          </NavLink>
        </li>
      </ul>

      <div className="right-nav">
        <NavLink to="/sign-in" id="sign-in-btn">Sign In</NavLink>
        <NavLink to="/content-detect" id="try-now-btn">Try Now</NavLink>
      </div>
    </nav>
  )
}