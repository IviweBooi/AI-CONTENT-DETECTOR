import { useState, useEffect, useRef } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import homeIcon from '../assets/icons/home.svg'
import bookIcon from '../assets/icons/book.svg'
import detectIcon from '../assets/icons/detect.svg'
import helpIcon from '../assets/icons/help.svg'
import signinIcon from '../assets/icons/signin.svg'
import userIcon from '../assets/icons/user.svg'

export default function NavBar() {
  const [open, setOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const { user, logout } = useAuth()
  const profileRef = useRef(null)

  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setProfileOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleLogout = async () => {
    try {
      await logout()
      setProfileOpen(false)
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

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

        {/* Mobile-only Sign In link inside menu - only show when not authenticated */}
        {!user && (
          <li className="mobile-only">
            <NavLink to="/sign-in" className={({ isActive }) => (isActive ? 'active' : undefined)}>
              <img src={signinIcon} alt="sign in" height="20" />
              <span>Sign In</span>
            </NavLink>
          </li>
        )}
        
        {/* Mobile-only user profile when authenticated */}
        {user && (
          <li className="mobile-only">
            <div className="mobile-profile-dropdown">
              <button 
                className="mobile-profile-trigger"
                onClick={() => setProfileOpen(!profileOpen)}
                aria-label="User menu"
              >
                <img src={userIcon} alt="profile" height="20" />
                <span>Profile</span>
                <i className={`fa-solid fa-chevron-down ${profileOpen ? 'rotate' : ''}`}></i>
              </button>
              
              {profileOpen && (
                <div className="mobile-profile-menu">
                  <div className="mobile-profile-info">
                    <p className="mobile-profile-name">{user.displayName || 'User'}</p>
                    <p className="mobile-profile-email">{user.email}</p>
                  </div>
                  <hr />
                  <button className="mobile-profile-menu-item" onClick={handleLogout}>
                    <i className="fa-solid fa-sign-out-alt"></i>
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </li>
        )}
      </ul>

      <div className="right-nav">
        {!user ? (
          // Show sign-in and try-now buttons when not authenticated
          <>
            <NavLink to="/sign-in" id="sign-in-btn">Sign In</NavLink>
            <NavLink to="/content-detect" id="try-now-btn">Try Now</NavLink>
          </>
        ) : (
          // Show user profile when authenticated
          <div className="profile-dropdown" ref={profileRef}>
            <button 
               className="profile-trigger"
               onClick={() => setProfileOpen(!profileOpen)}
               aria-label="User menu"
             >
               <img src={userIcon} alt="profile" height="20" />
               <i className={`fa-solid fa-chevron-down ${profileOpen ? 'rotate' : ''}`}></i>
             </button>
            
            {profileOpen && (
              <div className="profile-menu">
                <div className="profile-info">
                  <p className="profile-name">{user.displayName || 'User'}</p>
                  <p className="profile-email">{user.email}</p>
                </div>
                <hr />
                <button className="profile-menu-item" onClick={handleLogout}>
                  <i className="fa-solid fa-sign-out-alt"></i>
                  Sign Out
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}