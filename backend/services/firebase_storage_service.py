import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import tempfile

try:
    from services.firebase_service import get_firebase_service
    firebase_service = get_firebase_service()
except Exception as e:
    print(f"Warning: Firebase service not available in storage service: {e}")
    firebase_service = None

class FirebaseStorageService:
    """Service for handling file processing without permanent storage."""
    
    def __init__(self):
        self.firebase_service = firebase_service
        # Use temporary directory for file processing
        self.temp_folder = tempfile.gettempdir()
        
    def is_firebase_available(self):
        """Check if Firebase Storage is available (disabled for now)."""
        return False  # Disabled Firebase Storage
    
    def process_file(self, file, user_id=None):
        """Process a file temporarily without permanent storage.
        
        Args:
            file: Werkzeug FileStorage object
            user_id: Optional user ID for organizing files
            
        Returns:
            dict: Processing result with temporary file info
        """
        try:
            # Secure the filename
            filename = secure_filename(file.filename)
            if not filename:
                filename = f"file_{uuid.uuid4().hex}"
            
            # Create temporary file for processing
            temp_file_path = self._create_temp_file(file, filename)
            
            return {
                'success': True,
                'storage_type': 'temporary',
                'file_path': temp_file_path,
                'original_filename': filename,
                'file_size': os.path.getsize(temp_file_path) if os.path.exists(temp_file_path) else 0,
                'content_type': file.content_type,
                'processing_timestamp': datetime.now().isoformat(),
                'note': 'File processed temporarily - not permanently stored'
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"File processing failed: {str(e)}",
                'storage_type': 'error'
            }
    
    def _create_temp_file(self, file, original_filename):
        """Create a temporary file for processing."""
        try:
            # Create a temporary file with the original extension
            file_ext = os.path.splitext(original_filename)[1]
            temp_fd, temp_path = tempfile.mkstemp(suffix=file_ext, prefix='ai_detector_')
            
            # Close the file descriptor and save the uploaded file
            os.close(temp_fd)
            file.save(temp_path)
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"Temporary file creation failed: {str(e)}")
    
    def cleanup_temp_file(self, file_path):
        """Clean up a temporary file after processing.
        
        Args:
            file_path: Path to the temporary file
            
        Returns:
            dict: Cleanup result
        """
        try:
            if os.path.exists(file_path) and file_path.startswith(self.temp_folder):
                os.remove(file_path)
                return {
                    'success': True,
                    'message': 'Temporary file cleaned up successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'File not found or not a temporary file'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Cleanup failed: {str(e)}"
            }
    
    def get_file_content(self, file_path):
        """Read content from a temporary file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: File content or None if failed
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                return None
                
        except Exception as e:
            print(f"Failed to read file content: {str(e)}")
            return None
    
    # Legacy methods for backward compatibility (now disabled)
    def upload_file(self, file, folder='uploads', user_id=None):
        """Legacy upload method - now redirects to process_file."""
        return self.process_file(file, user_id)
    
    def delete_file(self, file_path, storage_type='auto'):
        """Legacy delete method - now redirects to cleanup_temp_file."""
        return self.cleanup_temp_file(file_path)
    
    def get_file_info(self, file_path, storage_type='auto'):
        """Get information about a temporary file.
        
        Args:
            file_path: Path to the file
            storage_type: Ignored (kept for compatibility)
            
        Returns:
            dict: File information
        """
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    'success': True,
                    'storage_type': 'temporary',
                    'file_path': file_path,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'updated': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'note': 'Temporary file - will be cleaned up after processing'
                }
            else:
                return {
                    'success': False,
                    'error': 'File not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get file info: {str(e)}"
            }

# Global instance
storage_service = FirebaseStorageService()

def get_storage_service():
    """Get the Firebase Storage service instance."""
    return storage_service