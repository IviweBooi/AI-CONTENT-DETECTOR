import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import detectIcon from '../assets/icons/detect.svg'

export default function SignUpPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }
    
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      console.log('Sign up data:', formData)
      setLoading(false)
      // In a real app, you would handle the signup logic here
      // and redirect on success
      // navigate('/dashboard')
      alert('Sign up successful! Redirecting to dashboard...')
    }, 1000)
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
              <img src={detectIcon} alt="" width="24" height="24" />
            </div>
            <h1 className="auth-title">Create an account</h1>
            <p className="auth-subtitle">Join us to get started</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="input-label" htmlFor="name">Full Name</label>
              <div className={`input-field ${errors.name ? 'error' : ''}`}>
                <i className="fa-regular fa-user" aria-hidden="true"></i>
                <input
                  id="name"
                  name="name"
                  type="text"
                  className="input"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={handleChange}
                />
              </div>
              {errors.name && <p className="error-message">{errors.name}</p>}
            </div>

            <div className="form-group">
              <label className="input-label" htmlFor="email">Email</label>
              <div className={`input-field ${errors.email ? 'error' : ''}`}>
                <i className="fa-regular fa-envelope" aria-hidden="true"></i>
                <input
                  id="email"
                  name="email"
                  type="email"
                  className="input"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
              {errors.email && <p className="error-message">{errors.email}</p>}
            </div>

            <div className="form-group">
              <label className="input-label" htmlFor="password">Password</label>
              <div className={`input-field ${errors.password ? 'error' : ''}`}>
                <i className="fa-solid fa-lock" aria-hidden="true"></i>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  className="input"
                  placeholder="Create a password"
                  value={formData.password}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="icon-btn"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  <i className={`fa-solid ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`} aria-hidden="true"></i>
                </button>
              </div>
              {errors.password && <p className="error-message">{errors.password}</p>}
            </div>

            <div className="form-group">
              <label className="input-label" htmlFor="confirmPassword">Confirm Password</label>
              <div className={`input-field ${errors.confirmPassword ? 'error' : ''}`}>
                <i className="fa-solid fa-lock" aria-hidden="true"></i>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  className="input"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
              </div>
              {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}
            </div>

            <div className="auth-row">
              <label className="check">
                <input type="checkbox" required />
                <span>I agree to the <Link to="/terms" className="link">Terms</Link> and <Link to="/privacy-policy" className="link">Privacy Policy</Link></span>
              </label>
            </div>

            <button 
              className="btn btn-primary auth-submit" 
              type="submit" 
              disabled={loading}
            >
              {loading ? (
                <span className="loading-spinner" />
              ) : (
                <i className="fa-solid fa-user-plus" aria-hidden="true"></i>
              )}
              <span>{loading ? 'Creating account...' : 'Sign up'}</span>
            </button>
          </form>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <div className="social-btns">
            <button type="button" className="btn btn-ghost">
              <i className="fa-brands fa-google"></i>
              <span>Continue with Google</span>
            </button>
            <button type="button" className="btn btn-ghost">
              <i className="fa-brands fa-github"></i>
              <span>Continue with GitHub</span>
            </button>
          </div>

          <p className="auth-footer">
            Already have an account?{' '}
            <Link to="/sign-in" className="link">Sign in</Link>
          </p>
        </div>
      </div>
    </section>
  )
}
