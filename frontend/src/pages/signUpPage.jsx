import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import detectIcon from '../assets/icons/detect.svg'

export default function SignUpPage() {
  const navigate = useNavigate()
  const { signUp, signInWithGoogle, signInWithGitHub, error, clearError } = useAuth()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [isInitialLoad, setIsInitialLoad] = useState(true)

  // Load saved form data on component mount
  useEffect(() => {
    const savedFormData = localStorage.getItem('signUpFormData')
    const savedAcceptTerms = localStorage.getItem('signUpAcceptTerms')
    
    if (savedFormData) {
      try {
        const parsedData = JSON.parse(savedFormData)
        setFormData(parsedData)
      } catch (error) {
        console.error('Error parsing saved form data:', error)
      }
    }
    
    if (savedAcceptTerms) {
      setAcceptTerms(savedAcceptTerms === 'true')
    }
    
    // Mark initial load as complete
    setIsInitialLoad(false)
  }, [])

  // Save form data to localStorage whenever it changes (but not on initial load)
  useEffect(() => {
    if (!isInitialLoad) {
      localStorage.setItem('signUpFormData', JSON.stringify(formData))
    }
  }, [formData, isInitialLoad])

  // Save acceptTerms to localStorage whenever it changes (but not on initial load)
  useEffect(() => {
    if (!isInitialLoad) {
      localStorage.setItem('signUpAcceptTerms', acceptTerms.toString())
    }
  }, [acceptTerms, isInitialLoad])

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
    // Real-time validation
    validateField(name, value)
  }

  // Real-time field validation
  const validateField = (name, value) => {
    const newErrors = { ...errors }
    
    switch (name) {
      case 'name':
        if (!value.trim()) {
          newErrors.name = 'Please enter your full name'
        } else if (value.trim().length < 2) {
          newErrors.name = 'Name must be at least 2 characters long'
        } else {
          delete newErrors.name
        }
        break
        
      case 'email':
        if (!value) {
          newErrors.email = 'Please enter your email address'
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          newErrors.email = 'Please enter a valid email address'
        } else {
          delete newErrors.email
        }
        break
        
      case 'password':
        if (!value) {
          newErrors.password = 'Please create a password'
        } else if (value.length < 8) {
          newErrors.password = 'Password must be at least 8 characters long'
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          newErrors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
        } else {
          delete newErrors.password
        }
        
        // Also validate confirm password if it exists
        if (formData.confirmPassword && value !== formData.confirmPassword) {
          newErrors.confirmPassword = 'Passwords do not match'
        } else if (formData.confirmPassword && value === formData.confirmPassword) {
          delete newErrors.confirmPassword
        }
        break
        
      case 'confirmPassword':
        if (!value) {
          newErrors.confirmPassword = 'Please confirm your password'
        } else if (value !== formData.password) {
          newErrors.confirmPassword = 'Passwords do not match'
        } else {
          delete newErrors.confirmPassword
        }
        break
    }
    
    setErrors(newErrors)
  }

  // Check if form is valid for button state
  const isFormValid = () => {
    return (
      formData.name.trim().length >= 2 &&
      formData.email &&
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email) &&
      formData.password.length >= 8 &&
      /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password) &&
      formData.password === formData.confirmPassword &&
      acceptTerms &&
      Object.keys(errors).length === 0
    )
  }

  // Validate form fields (for submission)
  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Please enter your full name'
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters long'
    }
    
    if (!formData.email) {
      newErrors.email = 'Please enter your email address'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }
    
    if (!formData.password) {
      newErrors.password = 'Please create a password'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long'
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password'
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return
    if (!acceptTerms) {
      setErrors({ terms: 'Please accept the Terms and Privacy Policy to continue' })
      return
    }

    setLoading(true)
    clearError()

    try {
      await signUp(formData.email, formData.password, formData.name)
      // Clear stored form data after successful submission
      localStorage.removeItem('signUpFormData')
      localStorage.removeItem('signUpAcceptTerms')
      // Show success message and redirect
      setShowSuccess(true)
      setTimeout(() => {
        navigate('/sign-in')
      }, 3000) // Navigate after 3 seconds to allow user to read the message
    } catch (error) {
      console.error('Sign up error:', error)
      // Handle specific Firebase errors with user-friendly messages
      let errorMessage = 'Something went wrong. Please try again.'
      
      if (error.code === 'auth/email-already-in-use') {
        errorMessage = 'An account with this email already exists. Please sign in instead.'
      } else if (error.code === 'auth/weak-password') {
        errorMessage = 'Please choose a stronger password.'
      } else if (error.code === 'auth/invalid-email') {
        errorMessage = 'Please enter a valid email address.'
      } else if (error.code === 'auth/network-request-failed') {
        errorMessage = 'Network error. Please check your connection and try again.'
      }
      
      setErrors({ general: errorMessage })
    } finally {
      setLoading(false)
    }
  }

  // Handle Google sign up
  async function handleGoogleSignUp() {
    setLoading(true)
    clearError()
    
    try {
      await signInWithGoogle()
      navigate('/dashboard')
    } catch (error) {
      console.error('Google sign up error:', error)
    } finally {
      setLoading(false)
    }
  }

  // Handle GitHub sign up
  async function handleGitHubSignUp() {
    setLoading(true)
    clearError()
    
    try {
      await signInWithGitHub()
      navigate('/dashboard')
    } catch (error) {
      console.error('GitHub sign up error:', error)
    } finally {
      setLoading(false)
    }
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

            {/* Confirm Password */}
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

            {(error || errors.general) && (
              <div className="error-message" style={{ color: '#ef4444', fontSize: '14px', marginBottom: '12px' }}>
                {errors.general || error}
              </div>
            )}

            <div className="auth-row">
              <label className="check">
                <input 
                  type="checkbox" 
                  checked={acceptTerms}
                  onChange={(e) => {
                    setAcceptTerms(e.target.checked)
                    if (errors.terms) {
                      setErrors(prev => ({ ...prev, terms: '' }))
                    }
                  }}
                  required 
                />
                <span>I agree to the <Link to="/terms" className="link">Terms</Link> and <Link to="/privacy-policy" className="link">Privacy Policy</Link></span>
              </label>
              {errors.terms && <p className="error-message">{errors.terms}</p>}
            </div>

            <button 
              className={`btn btn-primary auth-submit ${!isFormValid() || loading ? 'disabled' : ''}`}
              type="submit" 
              disabled={!isFormValid() || loading}
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
            <button 
              type="button" 
              className="btn btn-ghost"
              onClick={handleGoogleSignUp}
              disabled={loading}
            >
              <i className="fa-brands fa-google"></i>
              <span>Continue with Google</span>
            </button>
            <button 
              type="button" 
              className="btn btn-ghost"
              onClick={handleGitHubSignUp}
              disabled={loading}
            >
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

      {/* Success Message */}
      {showSuccess && (
        <div className="success-message">
          <div className="success-message-content">
            <i className="fa-solid fa-check-circle" aria-hidden="true"></i>
            <span>Account created successfully! Please check your email to verify your account.</span>
          </div>
        </div>
      )}
    </section>
  )
}
