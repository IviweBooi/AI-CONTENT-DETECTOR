import { createContext, useContext, useEffect, useState } from 'react'
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  updateProfile,
  sendPasswordResetEmail,
  GoogleAuthProvider,
  GithubAuthProvider,
  signInWithPopup,
  sendEmailVerification
} from 'firebase/auth'
import { doc, setDoc, getDoc, serverTimestamp } from 'firebase/firestore'
import { auth, db } from '../config/firebase'

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// Create Auth Context
const AuthContext = createContext({})

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Clear error helper
  const clearError = () => setError(null)

  // Create user profile in Firestore
  const createUserProfile = async (user, additionalData = {}) => {
    if (!user) return
    
    try {
      const userRef = doc(db, 'users', user.uid)
      const userSnap = await getDoc(userRef)
      
      if (!userSnap.exists()) {
        const { displayName, email, photoURL } = user
        const createdAt = serverTimestamp()
        
        await setDoc(userRef, {
          displayName: displayName || additionalData.name || '',
          email,
          photoURL: photoURL || '',
          createdAt,
          lastLoginAt: createdAt,
          emailVerified: user.emailVerified,
          ...additionalData
        })
        

      } else {
        // Update last login time
        await setDoc(userRef, {
          lastLoginAt: serverTimestamp(),
          emailVerified: user.emailVerified
        }, { merge: true })
      }
    } catch (error) {
      console.error('Error creating user profile:', error)
      throw error
    }
  }

  // Sign up with email and password
  const signUp = async (email, password, name) => {
    try {
      setError(null)
      setLoading(true)
      
      const { user } = await createUserWithEmailAndPassword(auth, email, password)
      
      // Update user profile with name
      if (name) {
        await updateProfile(user, {
          displayName: name
        })
      }
      
      // Send email verification with action URL
      const actionCodeSettings = {
        url: `${window.location.origin}/sign-in?verified=true`,
        handleCodeInApp: false
      }
      await sendEmailVerification(user, actionCodeSettings)
      
      // Create user profile in Firestore
      await createUserProfile(user, { name })
      
      return user
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // Sign in with email and password
  const signIn = async (email, password) => {
    try {
      setError(null)
      setLoading(true)
      
      const { user } = await signInWithEmailAndPassword(auth, email, password)
      
      // Update user profile
      await createUserProfile(user)
      
      return user
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // Sign in with Google
  const signInWithGoogle = async () => {
    try {
      setError(null)
      setLoading(true)
      
      const provider = new GoogleAuthProvider()
      provider.addScope('email')
      provider.addScope('profile')
      
      const { user } = await signInWithPopup(auth, provider)
      
      // Create user profile in Firestore
      await createUserProfile(user)
      
      return user
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // Sign in with GitHub
  const signInWithGitHub = async () => {
    try {
      setError(null)
      setLoading(true)
      
      const provider = new GithubAuthProvider()
      provider.addScope('user:email')
      
      const { user } = await signInWithPopup(auth, provider)
      
      // Create user profile in Firestore
      await createUserProfile(user)
      
      return user
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // Sign out
  const logout = async () => {
    try {
      setError(null)
      await signOut(auth)
    } catch (error) {
      setError(error.message)
      throw error
    }
  }

  // Reset password
  const resetPassword = async (email) => {
    try {
      setError(null)
      await sendPasswordResetEmail(auth, email)
    } catch (error) {
      setError(error.message)
      throw error
    }
  }

  // Update user profile
  const updateUserProfile = async (displayName, email) => {
    try {
      setError(null)
      setLoading(true)
      
      if (!auth.currentUser) {
        throw new Error('No user is currently signed in')
      }

      // Update Firebase Auth profile
      const updates = {}
      if (displayName !== undefined && displayName !== auth.currentUser.displayName) {
        updates.displayName = displayName
      }

      if (Object.keys(updates).length > 0) {
        await updateProfile(auth.currentUser, updates)
      }

      // Update email if provided and different
      if (email && email !== auth.currentUser.email) {
        // Note: updateEmail requires recent authentication
        // For now, we'll just update the display name
        // Email updates should be handled separately with re-authentication
        console.log('Email update requires re-authentication - not implemented yet')
      }

      // Update Firestore user document
      const userRef = doc(db, 'users', auth.currentUser.uid)
      const updateData = {
        updatedAt: serverTimestamp()
      }
      
      if (displayName !== undefined) {
        updateData.displayName = displayName
      }

      await setDoc(userRef, updateData, { merge: true })

      // Refresh user data
      await createUserProfile(auth.currentUser)

      return { success: true, message: 'Profile updated successfully' }
    } catch (error) {
      setError(error.message)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // Resend email verification
  const resendEmailVerification = async () => {
    try {
      setError(null)
      if (auth.currentUser) {
        const actionCodeSettings = {
          url: `${window.location.origin}/sign-in?verified=true`,
          handleCodeInApp: false
        }
        await sendEmailVerification(auth.currentUser, actionCodeSettings)
      }
    } catch (error) {
      setError(error.message)
      throw error
    }
  }

  // Get user token for API calls
  const getAuthToken = async () => {
    if (auth.currentUser) {
      return await auth.currentUser.getIdToken()
    }
    return null
  }

  // Disable user account
  const disableAccount = async () => {
    console.log('disableAccount function called')
    try {
      setError(null)
      const token = await getAuthToken()
      console.log('Token obtained:', token ? 'Yes' : 'No')
      console.log('API URL:', `${API_BASE_URL}/auth/user/disable`)
      
      const response = await fetch(`${API_BASE_URL}/auth/user/disable`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      console.log('Response status:', response.status)
      const data = await response.json()
      console.log('Response data:', data)

      if (!response.ok) {
        throw new Error(data.message || 'Failed to disable account')
      }

      return data
    } catch (error) {
      console.error('disableAccount error:', error)
      setError(error.message)
      throw error
    }
  }

  // Delete user account
  const deleteAccount = async () => {
    console.log('deleteAccount function called')
    try {
      setError(null)
      const token = await getAuthToken()
      console.log('Token obtained:', token ? 'Yes' : 'No')
      console.log('API URL:', `${API_BASE_URL}/auth/user/delete`)
      
      const response = await fetch(`${API_BASE_URL}/auth/user/delete`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      console.log('Response status:', response.status)
      const data = await response.json()
      console.log('Response data:', data)

      if (!response.ok) {
        throw new Error(data.message || 'Failed to delete account')
      }

      return data
    } catch (error) {
      console.error('deleteAccount error:', error)
      setError(error.message)
      throw error
    }
  }

  // Listen for auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      try {
        if (user) {
          // Update user profile on auth state change
          await createUserProfile(user)
        }
        setUser(user)
      } catch (error) {
        console.error('Error in auth state change:', error)
        setError(error.message)
      } finally {
        setLoading(false)
      }
    })

    return unsubscribe
  }, [])

  // Auth context value
  const value = {
    user,
    loading,
    error,
    signUp,
    signIn,
    signInWithGoogle,
    signInWithGitHub,
    logout,
    resetPassword,
    updateUserProfile,
    resendEmailVerification,
    getAuthToken,
    disableAccount,
    deleteAccount,
    clearError,
    isAuthenticated: !!user,
    isEmailVerified: user?.emailVerified || false
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext