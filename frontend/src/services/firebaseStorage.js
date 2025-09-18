// Firebase Storage service for file uploads - DISABLED FOR SIMPLIFIED APP
// This service is disabled to simplify the application and remove storage dependencies

/**
 * Firebase Storage Service - DISABLED
 * All methods now return errors indicating storage is disabled
 */
class FirebaseStorageService {
  constructor() {
    console.log('Firebase Storage service is disabled in simplified mode')
  }

  /**
   * Upload a file to Firebase Storage - DISABLED
   */
  async uploadFile(file, folder, userId, onProgress) {
    throw new Error('Firebase Storage is disabled in simplified mode. Files are processed temporarily.')
  }

  /**
   * Delete a file from Firebase Storage - DISABLED
   */
  async deleteFile(filePath) {
    throw new Error('Firebase Storage is disabled in simplified mode.')
  }

  /**
   * List files in a folder - DISABLED
   */
  async listFiles(folder, userId) {
    throw new Error('Firebase Storage is disabled in simplified mode.')
  }

  /**
   * Get download URL for a file - DISABLED
   */
  async getDownloadURL(filePath) {
    throw new Error('Firebase Storage is disabled in simplified mode.')
  }

  /**
   * Check if Firebase Storage is available - ALWAYS FALSE
   */
  isAvailable() {
    return false
  }
}

const firebaseStorageService = new FirebaseStorageService()

/**
 * React hook for Firebase Storage operations - DISABLED
 * @returns {Object} Storage service methods and state (all disabled)
 */
export const useFirebaseStorage = () => {
  const uploadFile = async (file, folder, onProgress) => {
    throw new Error('Firebase Storage is disabled in simplified mode. Files are processed temporarily.')
  }

  const deleteFile = async (filePath) => {
    throw new Error('Firebase Storage is disabled in simplified mode.')
  }

  const listFiles = async (folder) => {
    throw new Error('Firebase Storage is disabled in simplified mode.')
  }

  const getDownloadURL = async (filePath) => {
    throw new Error('Firebase Storage is disabled in simplified mode.')
  }

  return {
    uploadFile,
    deleteFile,
    listFiles,
    getDownloadURL,
    isAvailable: false, // Always false
  }
}

export default firebaseStorageService