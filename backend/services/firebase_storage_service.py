import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

try:
    from services.firebase_service import get_firebase_service
    firebase_service = get_firebase_service()
except Exception as e:
    print(f"Warning: Firebase service not available in storage service: {e}")
    firebase_service = None

class FirebaseStorageService:
    """Service for handling file uploads to Firebase Storage."""
    
    def __init__(self):
        self.firebase_service = firebase_service
        self.bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')
        self.local_upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        
        # Ensure local upload folder exists as fallback
        if not os.path.exists(self.local_upload_folder):
            os.makedirs(self.local_upload_folder)
    
    def is_firebase_available(self):
        """Check if Firebase Storage is available."""
        return self.firebase_service is not None and self.bucket_name is not None
    
    def upload_file(self, file, folder='uploads', user_id=None):
        """Upload a file to Firebase Storage or local storage as fallback.
        
        Args:
            file: Werkzeug FileStorage object
            folder: Storage folder/path
            user_id: Optional user ID for organizing files
            
        Returns:
            dict: Upload result with file info
        """
        try:
            # Secure the filename
            filename = secure_filename(file.filename)
            if not filename:
                filename = f"file_{uuid.uuid4().hex}"
            
            # Add timestamp and UUID to prevent conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
            
            # Construct storage path
            if user_id:
                storage_path = f"{folder}/{user_id}/{unique_filename}"
            else:
                storage_path = f"{folder}/{unique_filename}"
            
            if self.is_firebase_available():
                return self._upload_to_firebase(file, storage_path, filename)
            else:
                return self._upload_to_local(file, storage_path, filename)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Upload failed: {str(e)}",
                'storage_type': 'error'
            }
    
    def _upload_to_firebase(self, file, storage_path, original_filename):
        """Upload file to Firebase Storage."""
        try:
            # Upload to Firebase Storage
            blob = self.firebase_service.upload_file_to_storage(
                file, 
                storage_path,
                content_type=file.content_type
            )
            
            if not blob:
                raise Exception("Failed to upload to Firebase Storage")
            
            # Generate a signed URL for temporary access
            download_url = self.firebase_service.get_download_url(
                storage_path,
                expiration=timedelta(hours=24)
            )
            
            return {
                'success': True,
                'storage_type': 'firebase',
                'file_path': storage_path,
                'download_url': download_url,
                'original_filename': original_filename,
                'file_size': file.content_length or 0,
                'content_type': file.content_type,
                'upload_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Fallback to local storage if Firebase fails
            print(f"Firebase upload failed, falling back to local: {e}")
            return self._upload_to_local(file, storage_path, original_filename)
    
    def _upload_to_local(self, file, storage_path, original_filename):
        """Upload file to local storage as fallback."""
        try:
            # Create local directory structure
            local_path = os.path.join(self.local_upload_folder, storage_path)
            local_dir = os.path.dirname(local_path)
            
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            
            # Save file locally
            file.save(local_path)
            
            return {
                'success': True,
                'storage_type': 'local',
                'file_path': local_path,
                'download_url': None,  # No URL for local files
                'original_filename': original_filename,
                'file_size': os.path.getsize(local_path),
                'content_type': file.content_type,
                'upload_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Local upload failed: {str(e)}")
    
    def delete_file(self, file_path, storage_type='auto'):
        """Delete a file from storage.
        
        Args:
            file_path: Path to the file
            storage_type: 'firebase', 'local', or 'auto' to detect
            
        Returns:
            dict: Deletion result
        """
        try:
            if storage_type == 'auto':
                # Detect storage type based on path
                if file_path.startswith(self.local_upload_folder):
                    storage_type = 'local'
                else:
                    storage_type = 'firebase'
            
            if storage_type == 'firebase' and self.is_firebase_available():
                return self._delete_from_firebase(file_path)
            else:
                return self._delete_from_local(file_path)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Deletion failed: {str(e)}"
            }
    
    def _delete_from_firebase(self, storage_path):
        """Delete file from Firebase Storage."""
        try:
            success = self.firebase_service.delete_file_from_storage(storage_path)
            
            return {
                'success': success,
                'storage_type': 'firebase',
                'message': 'File deleted from Firebase Storage' if success else 'Failed to delete from Firebase Storage'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Firebase deletion failed: {str(e)}"
            }
    
    def _delete_from_local(self, file_path):
        """Delete file from local storage."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    'success': True,
                    'storage_type': 'local',
                    'message': 'File deleted from local storage'
                }
            else:
                return {
                    'success': False,
                    'error': 'File not found in local storage'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Local deletion failed: {str(e)}"
            }
    
    def get_file_info(self, file_path, storage_type='auto'):
        """Get information about a stored file.
        
        Args:
            file_path: Path to the file
            storage_type: 'firebase', 'local', or 'auto' to detect
            
        Returns:
            dict: File information
        """
        try:
            if storage_type == 'auto':
                if file_path.startswith(self.local_upload_folder):
                    storage_type = 'local'
                else:
                    storage_type = 'firebase'
            
            if storage_type == 'firebase' and self.is_firebase_available():
                return self._get_firebase_file_info(file_path)
            else:
                return self._get_local_file_info(file_path)
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get file info: {str(e)}"
            }
    
    def _get_firebase_file_info(self, storage_path):
        """Get file info from Firebase Storage."""
        try:
            file_info = self.firebase_service.get_file_metadata(storage_path)
            
            if file_info:
                return {
                    'success': True,
                    'storage_type': 'firebase',
                    'file_path': storage_path,
                    'size': file_info.get('size'),
                    'content_type': file_info.get('contentType'),
                    'created': file_info.get('timeCreated'),
                    'updated': file_info.get('updated')
                }
            else:
                return {
                    'success': False,
                    'error': 'File not found in Firebase Storage'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get Firebase file info: {str(e)}"
            }
    
    def _get_local_file_info(self, file_path):
        """Get file info from local storage."""
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    'success': True,
                    'storage_type': 'local',
                    'file_path': file_path,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'updated': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'File not found in local storage'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get local file info: {str(e)}"
            }

# Global instance
storage_service = FirebaseStorageService()

def get_storage_service():
    """Get the Firebase Storage service instance."""
    return storage_service