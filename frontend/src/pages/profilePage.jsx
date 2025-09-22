import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import '../styles/pages/profile.css'

export default function ProfilePage() {
  const { user, logout, disableAccount, deleteAccount, resetPassword } = useAuth()
  const navigate = useNavigate()
  const [showDisableModal, setShowDisableModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Redirect if not authenticated
  if (!user) {
    navigate('/sign-in')
    return null
  }

  const handleDisableAccount = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await disableAccount()
      setSuccess('Account disabled successfully. You will be signed out.')
      setTimeout(() => {
        logout()
        navigate('/sign-in')
      }, 2000)
    } catch (err) {
      setError(err.message || 'Failed to disable account')
    } finally {
      setLoading(false)
      setShowDisableModal(false)
    }
  }

  const handleDeleteAccount = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await deleteAccount()
      setSuccess('Account deleted successfully. You will be redirected to the homepage.')
      setTimeout(() => {
        logout()
        navigate('/')
      }, 2000)
    } catch (err) {
      setError(err.message || 'Failed to delete account')
    } finally {
      setLoading(false)
      setShowDeleteModal(false)
    }
  }

  const handleChangePassword = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await resetPassword(user.email)
      setSuccess('Password reset email sent successfully. Check your inbox.')
    } catch (err) {
      setError(err.message || 'Failed to send password reset email')
    } finally {
      setLoading(false)
    }
  }

  const handleEditProfile = () => {
    setShowEditModal(true)
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <h1>User Profile</h1>
          <p>Manage your account settings and preferences</p>
        </div>

        {/* User Information Section */}
        <div className="profile-section">
          <h2>Account Information</h2>
          <div className="user-info">
            <div className="info-item">
              <label>Name:</label>
              <span>{user.displayName || 'Not provided'}</span>
            </div>
            <div className="info-item">
              <label>Email:</label>
              <span>{user.email}</span>
            </div>
            <div className="info-item">
              <label>Email Verified:</label>
              <span className={user.emailVerified ? 'verified' : 'unverified'}>
                {user.emailVerified ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="info-item">
              <label>Account Created:</label>
              <span>{user.metadata?.creationTime ? new Date(user.metadata.creationTime).toLocaleDateString() : 'Unknown'}</span>
            </div>
          </div>
          
          {/* Profile Management Buttons */}
          <div className="profile-actions">
            <button 
              className="btn-edit-profile"
              onClick={handleEditProfile}
              disabled={loading}
            >
              <i className="fa-solid fa-edit"></i>
              Edit Profile
            </button>
            <button 
              className="btn-change-password"
              onClick={handleChangePassword}
              disabled={loading}
            >
              <i className="fa-solid fa-key"></i>
              Change Password
            </button>
          </div>
        </div>

        {/* Account Management Section */}
        <div className="profile-section danger-zone">
          <h2>Account Management</h2>
          <p className="danger-warning">
            <i className="fa-solid fa-triangle-exclamation"></i>
            These actions are permanent and cannot be undone.
          </p>

          <div className="account-actions">
            <div className="action-item">
              <div className="action-info">
                <h3>Disable Account</h3>
                <p>Temporarily disable your account. You can contact support to reactivate it later.</p>
              </div>
              <button 
                className="btn-disable"
                onClick={() => setShowDisableModal(true)}
                disabled={loading}
              >
                <i className="fa-solid fa-pause"></i>
                Disable Account
              </button>
            </div>

            <div className="action-item">
              <div className="action-info">
                <h3>Delete Account</h3>
                <p>Permanently delete your account and all associated data. This action cannot be undone.</p>
              </div>
              <button 
                className="btn-delete"
                onClick={() => setShowDeleteModal(true)}
                disabled={loading}
              >
                <i className="fa-solid fa-trash"></i>
                Delete Account
              </button>
            </div>
          </div>
        </div>

        {/* Status Messages */}
        {error && (
          <div className="error-message">
            <i className="fa-solid fa-circle-exclamation"></i>
            {error}
          </div>
        )}

        {success && (
          <div className="success-message">
            <i className="fa-solid fa-circle-check"></i>
            {success}
          </div>
        )}
      </div>

      {/* Disable Account Modal */}
      {showDisableModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Disable Account</h3>
              <button 
                className="modal-close"
                onClick={() => setShowDisableModal(false)}
                disabled={loading}
              >
                <i className="fa-solid fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p>Are you sure you want to disable your account?</p>
              <p>Your account will be temporarily disabled and you will be signed out. You can contact support to reactivate your account later.</p>
            </div>
            <div className="modal-actions">
              <button 
                className="btn-cancel"
                onClick={() => setShowDisableModal(false)}
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                className="btn-confirm-disable"
                onClick={handleDisableAccount}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <i className="fa-solid fa-spinner fa-spin"></i>
                    Disabling...
                  </>
                ) : (
                  <>
                    <i className="fa-solid fa-pause"></i>
                    Disable Account
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Delete Account</h3>
              <button 
                className="modal-close"
                onClick={() => setShowDeleteModal(false)}
                disabled={loading}
              >
                <i className="fa-solid fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p><strong>This action cannot be undone!</strong></p>
              <p>Are you sure you want to permanently delete your account?</p>
              <p>This will delete:</p>
              <ul>
                <li>Your user profile</li>
                <li>All your AI detection results</li>
                <li>All your feedback and data</li>
                <li>Everything associated with your account</li>
              </ul>
            </div>
            <div className="modal-actions">
              <button 
                className="btn-cancel"
                onClick={() => setShowDeleteModal(false)}
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                className="btn-confirm-delete"
                onClick={handleDeleteAccount}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <i className="fa-solid fa-spinner fa-spin"></i>
                    Deleting...
                  </>
                ) : (
                  <>
                    <i className="fa-solid fa-trash"></i>
                    Delete Account
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Profile Modal */}
      {showEditModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Edit Profile</h3>
              <button 
                className="modal-close"
                onClick={() => setShowEditModal(false)}
                disabled={loading}
              >
                <i className="fa-solid fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p><strong>Profile editing functionality coming soon!</strong></p>
              <p>This feature will allow you to:</p>
              <ul>
                <li>Update your display name</li>
                <li>Change your profile picture</li>
                <li>Update your preferences</li>
                <li>Manage notification settings</li>
              </ul>
              <p>For now, you can use the "Change Password" button to reset your password via email.</p>
            </div>
            <div className="modal-actions">
              <button 
                className="btn-cancel"
                onClick={() => setShowEditModal(false)}
                disabled={loading}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}