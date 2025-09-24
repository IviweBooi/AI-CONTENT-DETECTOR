// Firebase configuration and initialization
import { initializeApp } from 'firebase/app'
import { getAuth, connectAuthEmulator } from 'firebase/auth'
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore'

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  // storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET, // Disabled for simplified app
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
}

// Validate configuration (storage bucket no longer required)
const requiredEnvVars = [
  'VITE_FIREBASE_API_KEY',
  'VITE_FIREBASE_AUTH_DOMAIN',
  'VITE_FIREBASE_PROJECT_ID',
  // 'VITE_FIREBASE_STORAGE_BUCKET', // No longer required
  'VITE_FIREBASE_MESSAGING_SENDER_ID',
  'VITE_FIREBASE_APP_ID'
]

const missingVars = requiredEnvVars.filter(varName => !import.meta.env[varName])
if (missingVars.length > 0) {
  console.error('Missing required Firebase environment variables:', missingVars)
  console.error('Please check your .env file and ensure all Firebase configuration variables are set')
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize Firebase services (storage disabled)
export const auth = getAuth(app)
export const db = getFirestore(app)
// export const storage = getStorage(app) // Disabled for simplified app

// Connect to emulators in development (optional)
if (import.meta.env.DEV && import.meta.env.VITE_USE_FIREBASE_EMULATOR === 'true') {
  try {
    connectAuthEmulator(auth, 'http://localhost:9099')
    connectFirestoreEmulator(db, 'localhost', 8080)
    // connectStorageEmulator(storage, 'localhost', 9199) // Disabled

  } catch (error) {
    console.warn('Failed to connect to Firebase emulators:', error)
  }
}

// Export the app instance
export default app

// Helper function to check if Firebase is properly configured
export const isFirebaseConfigured = () => {
  return missingVars.length === 0
}

// Helper function to get current user
export const getCurrentUser = () => {
  return auth.currentUser
}

// Helper function to check if user is authenticated
export const isAuthenticated = () => {
  return !!auth.currentUser
}