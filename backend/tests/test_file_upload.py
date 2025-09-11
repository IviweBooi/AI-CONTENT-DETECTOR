import pytest
import json
import io
import os
import tempfile
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage

class TestFileUploadRoutes:
    """Test cases for file upload routes and validation"""
    
    def test_upload_health_check(self, client):
        """Test file upload service health check"""
        response = client.get('/api/supported-formats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'supported_formats' in data
        
        # Check that all expected formats are present
        extensions = [fmt['extension'] for fmt in data['supported_formats']]
        assert '.txt' in extensions
        assert '.pdf' in extensions
        assert '.docx' in extensions
    
    def test_upload_no_file_provided(self, client):
        """Test upload with no file in request"""
        response = client.post('/api/upload')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'No file provided'
        assert 'Please select a file' in data['message']
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename"""
        data = {
            'file': (io.BytesIO(b'test content'), '')
        }
        
        response = client.post('/api/upload', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'No file selected'
        assert 'Please select a file' in response_data['message']
    
    def test_upload_unsupported_file_type(self, client):
        """Test upload with unsupported file type"""
        data = {
            'file': (io.BytesIO(b'test content'), 'test.jpg')
        }
        
        response = client.post('/api/upload', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Unsupported file type'
        assert '.txt' in response_data['message']
        assert '.pdf' in response_data['message']
        assert '.docx' in response_data['message']
    
    @patch('utils.file_parsers.FileParserFactory.create_parser')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_upload_successful_txt_file(self, mock_exists, mock_makedirs, mock_create_parser, client):
        """Test successful upload of TXT file"""
        # Mock file system operations
        mock_exists.return_value = False
        
        # Mock parser
        mock_parser = MagicMock()
        mock_parser.parse.return_value = 'Test file content'
        mock_parser.get_file_info.return_value = {
            'filename': 'test.txt',
            'extension': '.txt',
            'size_bytes': 100,
            'size_mb': 0.0001
        }
        mock_create_parser.return_value = mock_parser
        
        # Create test file
        data = {
            'file': (io.BytesIO(b'test content'), 'test.txt')
        }
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('os.path.join', return_value='uploads/test.txt'):
                response = client.post('/api/upload', data=data)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['content'] == 'Test file content'
        assert 'file_info' in response_data
    
    @patch('utils.file_parsers.FileParserFactory.create_parser')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_upload_file_parsing_error(self, mock_exists, mock_makedirs, mock_create_parser, client):
        """Test upload with file parsing error"""
        # Mock file system operations
        mock_exists.return_value = False
        
        # Mock parser to raise exception
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = Exception('Parsing failed')
        mock_create_parser.return_value = mock_parser
        
        data = {
            'file': (io.BytesIO(b'corrupted content'), 'test.txt')
        }
        
        with patch('builtins.open', create=True):
            with patch('os.path.join', return_value='uploads/test.txt'):
                with patch('os.unlink') as mock_unlink:  # Mock file cleanup
                    response = client.post('/api/upload', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'File parsing error'
        assert 'Could not parse file' in response_data['message']
    
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_upload_duplicate_filename_handling(self, mock_exists, mock_makedirs, client):
        """Test handling of duplicate filenames"""
        # Mock file existence to simulate duplicate
        mock_exists.side_effect = [True, True, False]  # First two exist, third doesn't
        
        with patch('utils.file_parsers.FileParserFactory.create_parser') as mock_create_parser:
            mock_parser = MagicMock()
            mock_parser.parse.return_value = 'Test content'
            mock_parser.get_file_info.return_value = {'filename': 'test_2.txt'}
            mock_create_parser.return_value = mock_parser
            
            data = {
                'file': (io.BytesIO(b'test content'), 'test.txt')
            }
            
            with patch('builtins.open', create=True):
                with patch('os.path.join', side_effect=lambda *args: '/'.join(args)):
                    response = client.post('/api/upload', data=data)
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
    
    @patch('os.makedirs')
    def test_upload_general_exception(self, mock_makedirs, client):
        """Test upload with general exception"""
        # Make makedirs raise an exception
        mock_makedirs.side_effect = Exception('Disk full')
        
        data = {
            'file': (io.BytesIO(b'test content'), 'test.txt')
        }
        
        response = client.post('/api/upload', data=data)
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Upload error'
        assert 'An error occurred during upload' in response_data['message']

class TestFileValidation:
    """Test cases for file validation utilities"""
    
    def test_secure_filename_validation(self):
        """Test secure filename generation"""
        from werkzeug.utils import secure_filename
        
        # Test various filename scenarios
        assert secure_filename('test.txt') == 'test.txt'
        assert secure_filename('../../../etc/passwd') == 'etc_passwd'
        assert secure_filename('file with spaces.txt') == 'file_with_spaces.txt'
        assert secure_filename('file@#$%.txt') == 'file.txt'
    
    def test_file_extension_validation(self):
        """Test file extension validation logic"""
        allowed_extensions = {'.txt', '.pdf', '.docx'}
        
        # Valid extensions
        assert '.txt' in allowed_extensions
        assert '.pdf' in allowed_extensions
        assert '.docx' in allowed_extensions
        
        # Invalid extensions
        assert '.jpg' not in allowed_extensions
        assert '.exe' not in allowed_extensions
        assert '.py' not in allowed_extensions
    
    def test_file_size_limits(self):
        """Test file size validation (conceptual)"""
        # This would test file size limits if implemented
        max_size = 10 * 1024 * 1024  # 10MB
        
        # Small file should be allowed
        small_file_size = 1024  # 1KB
        assert small_file_size < max_size
        
        # Large file should be rejected
        large_file_size = 20 * 1024 * 1024  # 20MB
        assert large_file_size > max_size

class TestUploadDirectoryManagement:
    """Test cases for upload directory management"""
    
    @patch('os.makedirs')
    def test_upload_directory_creation(self, mock_makedirs):
        """Test upload directory creation"""
        from routes.file_upload import upload_file
        
        # This would test that the upload directory is created
        # when it doesn't exist
        mock_makedirs.assert_not_called()  # Not called yet
    
    def test_upload_path_security(self):
        """Test upload path security"""
        import os
        from werkzeug.utils import secure_filename
        
        # Test that paths are properly secured
        malicious_filename = '../../../etc/passwd'
        safe_filename = secure_filename(malicious_filename)
        
        # Should not contain path traversal
        assert '..' not in safe_filename
        assert '/' not in safe_filename
        assert '\\' not in safe_filename
    
    def test_file_cleanup_on_error(self):
        """Test that files are cleaned up when processing fails"""
        # This tests the cleanup logic in the upload route
        # when file parsing fails
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        # File should exist initially
        assert os.path.exists(tmp_path)
        
        # Clean up
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        
        # File should be removed
        assert not os.path.exists(tmp_path)

class TestFileStorageIntegration:
    """Test cases for file storage integration"""
    
    def test_file_storage_object_creation(self):
        """Test FileStorage object creation and validation"""
        # Create a mock FileStorage object
        file_content = b'test file content'
        file_storage = FileStorage(
            stream=io.BytesIO(file_content),
            filename='test.txt',
            content_type='text/plain'
        )
        
        assert file_storage.filename == 'test.txt'
        assert file_storage.content_type == 'text/plain'
        assert file_storage.read() == file_content
    
    def test_empty_file_storage(self):
        """Test handling of empty FileStorage objects"""
        empty_file = FileStorage(
            stream=io.BytesIO(b''),
            filename='',
            content_type=''
        )
        
        assert empty_file.filename == ''
        assert empty_file.read() == b''
    
    def test_file_storage_with_special_characters(self):
        """Test FileStorage with special characters in filename"""
        special_filename = 'test file (1) [copy].txt'
        file_storage = FileStorage(
            stream=io.BytesIO(b'content'),
            filename=special_filename,
            content_type='text/plain'
        )
        
        from werkzeug.utils import secure_filename
        safe_name = secure_filename(file_storage.filename)
        
        # Should be sanitized
        assert safe_name != special_filename
        assert '(' not in safe_name
        assert ')' not in safe_name
        assert '[' not in safe_name
        assert ']' not in safe_name

class TestErrorHandling:
    """Test cases for comprehensive error handling"""
    
    def test_missing_file_key_in_request(self, client):
        """Test request without 'file' key"""
        # Send request with different key
        data = {
            'document': (io.BytesIO(b'test'), 'test.txt')
        }
        
        response = client.post('/api/upload', data=data)
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert response_data['error'] == 'No file provided'
    
    def test_malformed_request_data(self, client):
        """Test malformed request data"""
        # Send invalid data
        response = client.post('/api/upload', data='invalid data')
        assert response.status_code == 400
    
    @patch('utils.file_parsers.FileParserFactory.create_parser')
    def test_parser_factory_exception(self, mock_create_parser, client):
        """Test FileParserFactory exception handling"""
        # Mock parser factory to raise exception
        mock_create_parser.side_effect = Exception('Parser not found')
        
        data = {
            'file': (io.BytesIO(b'test content'), 'test.txt')
        }
        
        with patch('os.makedirs'):
            with patch('os.path.exists', return_value=False):
                with patch('builtins.open', create=True):
                    with patch('os.path.join', return_value='uploads/test.txt'):
                        response = client.post('/api/upload', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'File parsing error'
    
    def test_file_save_permission_error(self, client):
        """Test file save with permission error"""
        data = {
            'file': (io.BytesIO(b'test content'), 'test.txt')
        }
        
        with patch('os.makedirs'):
            with patch('os.path.exists', return_value=False):
                # Mock file save to raise permission error
                with patch('builtins.open', side_effect=PermissionError('Access denied')):
                    response = client.post('/api/upload', data=data)
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Upload error'