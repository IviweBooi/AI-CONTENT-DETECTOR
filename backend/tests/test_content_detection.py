import pytest
import json
import io
import os
from unittest.mock import patch, MagicMock

class TestContentDetection:
    """Test cases for content detection routes"""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'content_detection'
        assert '.txt' in data['supported_formats']
        assert '.pdf' in data['supported_formats']
        assert '.docx' in data['supported_formats']
    
    @patch('routes.content_detection.detect_ai_content')
    def test_detect_text_success(self, mock_detect, client):
        """Test successful text detection"""
        # Mock AI detection response
        mock_detect.return_value = {
            'is_ai_generated': False,
            'confidence': 0.3,
            'analysis': {
                'perplexity_score': 45.2,
                'burstiness_score': 0.7
            }
        }
        
        response = client.post('/api/detect',
                             json={'text': 'This is a sample text for testing.'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['source'] == 'text_input'
        assert 'result' in data
        assert data['result']['is_ai_generated'] is False
        mock_detect.assert_called_once_with('This is a sample text for testing.')
    
    def test_detect_empty_text(self, client):
        """Test detection with empty text"""
        response = client.post('/api/detect',
                             json={'text': ''},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Empty text'
        assert 'Please provide text to analyze' in data['message']
    
    def test_detect_whitespace_only_text(self, client):
        """Test detection with whitespace-only text"""
        response = client.post('/api/detect',
                             json={'text': '   \n\t  '},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Empty text'
    
    @patch('routes.content_detection.detect_ai_content')
    @patch('routes.content_detection.FileParserFactory.create_parser')
    def test_detect_file_success(self, mock_parser_factory, mock_detect, client):
        """Test successful file detection"""
        # Mock file parser
        mock_parser = MagicMock()
        mock_parser.parse.return_value = 'Extracted text from file'
        mock_parser_factory.return_value = mock_parser
        
        # Mock AI detection
        mock_detect.return_value = {
            'is_ai_generated': True,
            'confidence': 0.8,
            'analysis': {'perplexity_score': 15.2}
        }
        
        # Create test file
        data = {
            'file': (io.BytesIO(b'test file content'), 'test.txt')
        }
        
        response = client.post('/api/detect', data=data)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['source'] == 'file_upload'
        assert response_data['filename'] == 'test.txt'
        assert response_data['file_type'] == '.txt'
        assert response_data['content'] == 'Extracted text from file'
        assert 'result' in response_data
        
        mock_detect.assert_called_once_with('Extracted text from file')
    
    def test_detect_no_file_selected(self, client):
        """Test detection with no file selected"""
        data = {
            'file': (io.BytesIO(b''), '')
        }
        
        response = client.post('/api/detect', data=data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'No file selected'
    
    def test_detect_unsupported_file_type(self, client):
        """Test detection with unsupported file type"""
        data = {
            'file': (io.BytesIO(b'test content'), 'test.jpg')
        }
        
        response = client.post('/api/detect', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Unsupported file type'
        assert '.txt' in response_data['message']
        assert '.pdf' in response_data['message']
        assert '.docx' in response_data['message']
    
    @patch('routes.content_detection.FileParserFactory.create_parser')
    def test_detect_empty_file_content(self, mock_parser_factory, client):
        """Test detection with file that has empty content"""
        # Mock file parser to return empty text
        mock_parser = MagicMock()
        mock_parser.parse.return_value = ''
        mock_parser_factory.return_value = mock_parser
        
        data = {
            'file': (io.BytesIO(b''), 'empty.txt')
        }
        
        response = client.post('/api/detect', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Empty file'
    
    @patch('routes.content_detection.FileParserFactory.create_parser')
    def test_detect_file_parsing_error(self, mock_parser_factory, client):
        """Test detection when file parsing fails"""
        # Mock file parser to raise an exception
        mock_parser_factory.side_effect = Exception('File parsing failed')
        
        data = {
            'file': (io.BytesIO(b'test content'), 'test.txt')
        }
        
        response = client.post('/api/detect', data=data)
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['error'] == 'Processing error'
        assert 'File parsing failed' in response_data['message']
    
    def test_detect_invalid_request(self, client):
        """Test detection with neither text nor file"""
        response = client.post('/api/detect',
                             json={'invalid': 'data'},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Invalid request'
        assert 'Please provide either text or a file' in data['message']
    
    @patch('routes.content_detection.detect_ai_content')
    def test_detect_ai_detection_error(self, mock_detect, client):
        """Test detection when AI detection fails"""
        # Mock AI detection to raise an exception
        mock_detect.side_effect = Exception('AI detection failed')
        
        response = client.post('/api/detect',
                             json={'text': 'Test text'},
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['error'] == 'Processing error'
        assert 'AI detection failed' in data['message']
    
    def test_detect_malformed_json(self, client):
        """Test detection with malformed JSON"""
        response = client.post('/api/detect',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['error'] == 'Processing error'