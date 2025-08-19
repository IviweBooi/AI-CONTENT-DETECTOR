import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function SignInPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  function onSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      alert('Demo sign-in. Hook up your auth logic here.')
    }, 800)
  }

  return (
    <section className="auth-section">
      <div className="auth-bg" aria-hidden="true" />
      <button
        type="button"
        className="btn btn-ghost auth-back"
        onClick={() => navigate(-1)}
        aria-label="Go back"
      >
        <i className="fa-solid fa-arrow-left" aria-hidden="true"></i>
        <span>Back</span>
      </button>
      <div className="auth-container">
        <div className="auth-card glass-card">
          <div className="auth-header">
            <div className="auth-logo" aria-hidden>
              <i className="fa-solid fa-magnifying-glass"></i>
            </div>
            <h1 className="auth-title">Welcome back</h1>
            <p className="auth-subtitle">Sign in to continue to your dashboard</p>
          </div>

          <form className="auth-form" onSubmit={onSubmit}>
            <label className="input-label" htmlFor="email">Email</label>
            <div className="input-field">
              <i className="fa-regular fa-envelope" aria-hidden="true"></i>
              <input
                id="email"
                type="email"
                className="input"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <label className="input-label" htmlFor="password">Password</label>
            <div className="input-field">
              <i className="fa-solid fa-lock" aria-hidden="true"></i>
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                className="input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="icon-btn"
                onClick={() => setShowPassword((s) => !s)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                <i className={`fa-solid ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`} aria-hidden="true"></i>
              </button>
            </div>

            <div className="auth-row">
              <label className="check">
                <input type="checkbox" />
                <span>Remember me</span>
              </label>
              <a className="muted-link" href="#">Forgot password?</a>
            </div>

            <button className="btn btn-primary auth-submit" type="submit" disabled={loading}>
              {loading ? <span className="loading-spinner" /> : <i className="fa-solid fa-right-to-bracket" aria-hidden="true"></i>}
              <span>{loading ? 'Signing in…' : 'Sign in'}</span>
            </button>
          </form>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <div className="social-btns">
            <button className="btn btn-ghost"><i className="fa-brands fa-google"></i><span>Continue with Google</span></button>
            <button className="btn btn-ghost"><i className="fa-brands fa-github"></i><span>Continue with GitHub</span></button>
          </div>

          <p className="auth-footer">Don’t have an account? <a href="#" className="link">Create one</a></p>
        </div>
      </div>
    </section>
  )
}
