import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

export default function EmailVerificationBanner() {
  const { user, resendEmailVerification } = useAuth()
  const [isResending, setIsResending] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [showBanner, setShowBanner] = useState(true)

  // Don't show banner if user is verified or banner is dismissed
  if (!user || user.emailVerified || !showBanner) {
    return null
  }

  const handleResendEmail = async () => {
    try {
      setIsResending(true)
      await resendEmailVerification()
      setShowSuccess(true)
      setTimeout(() => setShowSuccess(false), 5000) // Hide success message after 5 seconds
    } catch (error) {
      console.error('Error resending verification email:', error)
    } finally {
      setIsResending(false)
    }
  }

  const handleDismiss = () => {
    setShowBanner(false)
  }

  return (
    <div className="email-verification-banner">
      <div className="banner-content">
        <div className="banner-icon">
          <i className="fa-solid fa-envelope" aria-hidden="true"></i>
        </div>
        <div className="banner-text">
          <h4>Please verify your email address</h4>
          <p>
            We sent a verification email to <strong>{user.email}</strong>. 
            Please check your inbox and spam folder.
          </p>
        </div>
        <div className="banner-actions">
          {showSuccess ? (
            <span className="success-text">
              <i className="fa-solid fa-check" aria-hidden="true"></i>
              Email sent!
            </span>
          ) : (
            <button
              type="button"
              className="btn btn-sm btn-primary"
              onClick={handleResendEmail}
              disabled={isResending}
            >
              {isResending ? (
                <>
                  <span className="loading-spinner" />
                  Sending...
                </>
              ) : (
                <>
                  <i className="fa-solid fa-paper-plane" aria-hidden="true"></i>
                  Resend Email
                </>
              )}
            </button>
          )}
          <button
            type="button"
            className="btn btn-sm btn-ghost"
            onClick={handleDismiss}
            aria-label="Dismiss banner"
          >
            <i className="fa-solid fa-times" aria-hidden="true"></i>
          </button>
        </div>
      </div>
    </div>
  )
}