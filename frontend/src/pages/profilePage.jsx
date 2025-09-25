import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import '../styles/pages/profile.css'

export default function ProfilePage() {
  const { user, logout, disableAccount, deleteAccount, resetPassword, updateUserProfile } = useAuth()
  const navigate = useNavigate()
  const [showDisableModal, setShowDisableModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  // Edit profile form state
  const [editForm, setEditForm] = useState({
    displayName: '',
    email: ''
  })
  const [editLoading, setEditLoading] = useState(false)
  const [editError, setEditError] = useState('')
  const [editSuccess, setEditSuccess] = useState('')

  // Redirect if not authenticated
  useEffect(() => {
    if (!user) {
      navigate('/sign-in')
    }
  }, [user, navigate])

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
      console.error('disableAccount error:', err)
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
      console.error('deleteAccount error:', err)
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
    // Initialize form with current user data
    setEditForm({
      displayName: user?.displayName || '',
      email: user?.email || ''
    })
    setEditError('')
    setEditSuccess('')
    setShowEditModal(true)
  }

  const handleEditFormChange = (e) => {
    const { name, value } = e.target
    setEditForm(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleEditFormSubmit = async (e) => {
    e.preventDefault()
    setEditLoading(true)
    setEditError('')
    setEditSuccess('')

    try {
      // Basic validation
      if (!editForm.displayName.trim()) {
        throw new Error('Display name is required')
      }

      if (editForm.displayName.trim().length < 2) {
        throw new Error('Display name must be at least 2 characters long')
      }

      // Update profile
      await updateUserProfile(editForm.displayName.trim(), editForm.email.trim())
      setEditSuccess('Profile updated successfully!')
      
      // Close modal after a short delay
      setTimeout(() => {
        setShowEditModal(false)
      }, 1500)
    } catch (err) {
      setEditError(err.message || 'Failed to update profile')
    } finally {
      setEditLoading(false)
    }
  }

  // Don't render anything if user is not authenticated (will redirect)
  // Temporarily commented out to debug modal issue
  // if (!user) {
  //   return null
  // }

  return (
    <div className="profile-page">
      {/* Only render user content if user exists */}
      {user && (
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
      )}

      {/* Disable Account Modal */}
      {showDisableModal && (
        <div className="modal-overlay open">
          <div className="modal">
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
        <div className="modal-overlay open">
          <div className="modal">
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
        <div className="modal-overlay open">
          <div className="modal">
            <div className="modal-header">
              <h3>Edit Profile</h3>
              <button 
                className="modal-close"
                onClick={() => setShowEditModal(false)}
                disabled={editLoading}
              >
                <i className="fa-solid fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleEditFormSubmit}>
                <div className="form-group">
                  <label htmlFor="displayName" className="form-label">Display Name</label>
                  <input
                    type="text"
                    id="displayName"
                    name="displayName"
                    className="form-control"
                    value={editForm.displayName}
                    onChange={handleEditFormChange}
                    disabled={editLoading}
                    placeholder="Enter your display name"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="email" className="form-label">Email Address</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    className="form-control"
                    value={editForm.email}
                    onChange={handleEditFormChange}
                    disabled={true}
                    placeholder="Email updates require re-authentication"
                    title="Email updates require re-authentication and are not currently supported"
                  />
                  <small className="form-note">
                    Email updates require re-authentication and are not currently supported. 
                    Use "Change Password" to reset your password via email.
                  </small>
                </div>

                {editError && (
                  <div className="error-message">
                    <i className="fa-solid fa-exclamation-triangle"></i>
                    {editError}
                  </div>
                )}

                {editSuccess && (
                  <div className="success-message">
                    <i className="fa-solid fa-check-circle"></i>
                    {editSuccess}
                  </div>
                )}

                <div className="modal-actions">
                  <button 
                    type="button"
                    className="btn-cancel"
                    onClick={() => setShowEditModal(false)}
                    disabled={editLoading}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit"
                    className="btn btn-primary"
                    disabled={editLoading}
                  >
                    {editLoading ? (
                      <>
                        <i className="fa-solid fa-spinner fa-spin"></i>
                        Updating...
                      </>
                    ) : (
                      <>
                        <i className="fa-solid fa-save"></i>
                        Save Changes
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}