import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import detectIcon from '../assets/icons/detect.svg'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [errors, setErrors] = useState({})
  
  const { resetPassword, error, clearError } = useAuth()
  const navigate = useNavigate()

  // Validate email
  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!email) {
      return 'Email is required'
    }
    if (!emailRegex.test(email)) {
      return 'Please enter a valid email address'
    }
    return ''
  }

  // Handle email change
  const handleEmailChange = (e) => {
    const value = e.target.value
    setEmail(value)
    
    // Clear previous errors
    if (error) {
      clearError()
    }
    
    // Validate email
    const emailError = validateEmail(value)
    setErrors(prev => ({ ...prev, email: emailError }))
  }

  // Check if form is valid
  const isFormValid = () => {
    const hasValidEmail = email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    const hasNoErrors = !errors.email || errors.email === ''
    return hasValidEmail && hasNoErrors
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!isFormValid()) return

    try {
      setLoading(true)
      await resetPassword(email)
      setSuccess(true)
    } catch (err) {
      console.error('Password reset error:', err)
    } finally {
      setLoading(false)
    }
  }

  // If success, show success message
  if (success) {
    return (
      <section className="auth-section">
        <div className="auth-bg" aria-hidden="true" />
        <button
          type="button"
          className="btn btn-ghost auth-back"
          onClick={() => navigate('/sign-in')}
          aria-label="Back to sign in"
        >
          <i className="fa-solid fa-arrow-left" aria-hidden="true"></i>
          <span>Back to Sign In</span>
        </button>
        <div className="auth-container">
          <div className="auth-card glass-card">
            <div className="auth-header">
              <div className="auth-logo" aria-hidden>
                <img src={detectIcon} alt="" width="24" height="24" />
              </div>
              <h1 className="auth-title">Check your email</h1>
              <p className="auth-subtitle">
                We've sent a password reset link to <strong>{email}</strong>
              </p>
            </div>

            <div className="success-content">
              <div className="success-icon">
                <i className="fa-solid fa-envelope-circle-check" aria-hidden="true"></i>
              </div>
              
              <div className="success-message">
                <h3>Password reset email sent!</h3>
                <p className="success-description">
                  We've sent a password reset link to your email address.
                </p>
              </div>

              <div className="instruction-steps">
                <div className="step-item">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h4>Check your inbox</h4>
                    <p>Look for an email from our system with the subject "Reset your password"</p>
                  </div>
                </div>
                
                <div className="step-item">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h4>Click the reset link</h4>
                    <p>Follow the link in the email to create a new password</p>
                  </div>
                </div>
                
                <div className="step-item">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h4>Check spam folder</h4>
                    <p>If you don't see the email, please check your spam or junk folder</p>
                  </div>
                </div>
              </div>

              <div className="help-section">
                <div className="help-icon">
                  <i className="fa-solid fa-circle-question" aria-hidden="true"></i>
                </div>
                <div className="help-content">
                  <h4>Didn't receive the email?</h4>
                  <p>Try checking your spam folder or click "Send another email" below to resend the reset link.</p>
                </div>
              </div>
            </div>

            <div className="auth-actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setSuccess(false)}
              >
                <i className="fa-solid fa-paper-plane" aria-hidden="true"></i>
                <span>Send another email</span>
              </button>
              <Link to="/sign-in" className="btn btn-ghost">
                <i className="fa-solid fa-arrow-left" aria-hidden="true"></i>
                <span>Back to Sign In</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
    )
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
            <h1 className="auth-title">Reset your password</h1>
            <p className="auth-subtitle">
              Enter your email address and we'll send you a link to reset your password
            </p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="input-label" htmlFor="email">Email address</label>
              <div className={`input-field ${errors.email ? 'error' : ''}`}>
                <i className="fa-regular fa-envelope" aria-hidden="true"></i>
                <input
                  id="email"
                  type="email"
                  className="input"
                  placeholder="you@example.com"
                  value={email}
                  onChange={handleEmailChange}
                  required
                  autoFocus
                />
              </div>
              {errors.email && <p className="error-message">{errors.email}</p>}
            </div>

            {error && (
              <div className="error-message" style={{ color: '#ef4444', fontSize: '14px', marginBottom: '12px' }}>
                {error}
              </div>
            )}

            <button 
              className={`btn btn-primary auth-submit ${!isFormValid() || loading ? 'disabled' : ''}`}
              type="submit" 
              disabled={!isFormValid() || loading}
            >
              {loading ? <span className="loading-spinner" /> : <i className="fa-solid fa-paper-plane" aria-hidden="true"></i>}
              <span>{loading ? 'Sending reset email…' : 'Send reset email'}</span>
            </button>
          </form>

          <div className="auth-footer">
            <p>
              Remember your password? <Link to="/sign-in" className="auth-link">Sign in</Link>
            </p>
            <p>
              Don't have an account? <Link to="/sign-up" className="auth-link">Sign up</Link>
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}