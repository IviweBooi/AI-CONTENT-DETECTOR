// Firebase Storage service for file uploads
import { ref, uploadBytes, getDownloadURL, deleteObject, listAll } from 'firebase/storage'
import { storage, isFirebaseConfigured } from '../config/firebase'
import { useAuth } from '../contexts/AuthContext'

/**
 * Firebase Storage Service
 * Handles file uploads, downloads, and management
 */
class FirebaseStorageService {
  constructor() {
    this.storage = storage
    this.isConfigured = isFirebaseConfigured()
  }

  /**
   * Upload a file to Firebase Storage
   * @param {File} file - The file to upload
   * @param {string} folder - Storage folder (e.g., 'uploads', 'documents')
   * @param {string} userId - User ID for organizing files
   * @param {Function} onProgress - Progress callback function
   * @returns {Promise<Object>} Upload result with download URL
   */
  async uploadFile(file, folder = 'uploads', userId = null, onProgress = null) {
    if (!this.isConfigured) {
      throw new Error('Firebase Storage is not configured. Please check your environment variables.')
    }

    if (!file) {
      throw new Error('No file provided for upload')
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      throw new Error('File size exceeds 10MB limit')
    }

    // Validate file type
    const allowedTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Unsupported file type. Please upload TXT, PDF, or DOCX files only.')
    }

    try {
      // Create file path
      const timestamp = Date.now()
      const sanitizedFileName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_')
      const fileName = `${timestamp}_${sanitizedFileName}`
      
      let filePath
      if (userId) {
        filePath = `${folder}/${userId}/${fileName}`
      } else {
        filePath = `${folder}/anonymous/${fileName}`
      }

      // Create storage reference
      const storageRef = ref(this.storage, filePath)

      // Upload file
      const snapshot = await uploadBytes(storageRef, file)
      
      // Get download URL
      const downloadURL = await getDownloadURL(snapshot.ref)

      return {
        success: true,
        downloadURL,
        filePath,
        fileName: sanitizedFileName,
        originalName: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString()
      }
    } catch (error) {
      console.error('Firebase Storage upload error:', error)
      throw new Error(`Upload failed: ${error.message}`)
    }
  }

  /**
   * Delete a file from Firebase Storage
   * @param {string} filePath - Path to the file in storage
   * @returns {Promise<boolean>} Success status
   */
  async deleteFile(filePath) {
    if (!this.isConfigured) {
      throw new Error('Firebase Storage is not configured')
    }

    try {
      const storageRef = ref(this.storage, filePath)
      await deleteObject(storageRef)
      return true
    } catch (error) {
      console.error('Firebase Storage delete error:', error)
      throw new Error(`Delete failed: ${error.message}`)
    }
  }

  /**
   * List files in a folder
   * @param {string} folder - Folder path
   * @param {string} userId - User ID for filtering
   * @returns {Promise<Array>} List of file metadata
   */
  async listFiles(folder = 'uploads', userId = null) {
    if (!this.isConfigured) {
      throw new Error('Firebase Storage is not configured')
    }

    try {
      let folderPath = folder
      if (userId) {
        folderPath = `${folder}/${userId}`
      }

      const storageRef = ref(this.storage, folderPath)
      const result = await listAll(storageRef)
      
      const files = await Promise.all(
        result.items.map(async (itemRef) => {
          const downloadURL = await getDownloadURL(itemRef)
          return {
            name: itemRef.name,
            fullPath: itemRef.fullPath,
            downloadURL
          }
        })
      )

      return files
    } catch (error) {
      console.error('Firebase Storage list error:', error)
      throw new Error(`List files failed: ${error.message}`)
    }
  }

  /**
   * Get file download URL
   * @param {string} filePath - Path to the file
   * @returns {Promise<string>} Download URL
   */
  async getDownloadURL(filePath) {
    if (!this.isConfigured) {
      throw new Error('Firebase Storage is not configured')
    }

    try {
      const storageRef = ref(this.storage, filePath)
      return await getDownloadURL(storageRef)
    } catch (error) {
      console.error('Firebase Storage URL error:', error)
      throw new Error(`Get URL failed: ${error.message}`)
    }
  }

  /**
   * Check if Firebase Storage is available
   * @returns {boolean} Configuration status
   */
  isAvailable() {
    return this.isConfigured
  }
}

// Create and export singleton instance
const firebaseStorageService = new FirebaseStorageService()

/**
 * React hook for Firebase Storage operations
 * @returns {Object} Storage service methods and state
 */
export const useFirebaseStorage = () => {
  const { user } = useAuth()
  
  const uploadFile = async (file, folder = 'uploads', onProgress = null) => {
    return await firebaseStorageService.uploadFile(file, folder, user?.uid, onProgress)
  }

  const deleteFile = async (filePath) => {
    return await firebaseStorageService.deleteFile(filePath)
  }

  const listUserFiles = async (folder = 'uploads') => {
    return await firebaseStorageService.listFiles(folder, user?.uid)
  }

  const getFileURL = async (filePath) => {
    return await firebaseStorageService.getDownloadURL(filePath)
  }

  return {
    uploadFile,
    deleteFile,
    listUserFiles,
    getFileURL,
    isAvailable: firebaseStorageService.isAvailable(),
    userId: user?.uid
  }
}

export default firebaseStorageService