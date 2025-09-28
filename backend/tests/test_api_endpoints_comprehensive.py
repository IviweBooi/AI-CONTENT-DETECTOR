"""
Comprehensive unit tests for API endpoints
Tests the main API endpoints including content detection, file upload, and error handling.
"""

import pytest
import unittest
from unittest.mock import patch, MagicMock
import json
import io
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from routes.content_detection import content_detection_bp


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Sample test data
        self.valid_text = "This is a sample text for testing AI detection. It contains enough content to perform meaningful analysis and should trigger the detection algorithms properly."
        self.short_text = "Hi"
        self.empty_text = ""
        self.ai_like_text = "As an AI language model, I can provide you with comprehensive information about this topic. The implementation requires careful consideration of various factors."
        
        # Sample file content
        self.sample_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        self.sample_txt_content = b"This is a sample text file content for testing."
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_detect_endpoint_valid_text(self):
        """Test content detection with valid text"""
        response = self.client.post(
            '/api/detect',
            json={'text': self.valid_text},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('success', data)
        self.assertIn('result', data)
        self.assertIn('source', data)
        self.assertTrue(data['success'])
        self.assertEqual(data['source'], 'text_input')
        
        # Check result structure
        result = data['result']
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('confidence', result)
        self.assertIn('classification', result)
        self.assertIn('risk_level', result)
        
        # Check data types and ranges
        self.assertIsInstance(result['ai_probability'], float)
        self.assertIsInstance(result['human_probability'], float)
        self.assertIsInstance(result['confidence'], float)
        self.assertIsInstance(result['classification'], str)
        self.assertIsInstance(result['risk_level'], str)
        
        self.assertGreaterEqual(result['ai_probability'], 0.0)
        self.assertLessEqual(result['ai_probability'], 1.0)
        self.assertGreaterEqual(result['human_probability'], 0.0)
        self.assertLessEqual(result['human_probability'], 1.0)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
    
    def test_detect_endpoint_empty_text(self):
        """Test content detection with empty text"""
        response = self.client.post(
            '/api/detect',
            json={'text': self.empty_text},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        
        self.assertIn('error', data)
        self.assertIn('message', data)
        self.assertEqual(data['error'], 'Empty text')
    
    def test_detect_endpoint_no_text_field(self):
        """Test content detection without text field"""
        response = self.client.post(
            '/api/detect',
            json={'content': self.valid_text},  # Wrong field name
            content_type='application/json'
        )
        
        # Should handle missing text field gracefully
        self.assertIn(response.status_code, [400, 422])
    
    def test_detect_endpoint_invalid_json(self):
        """Test content detection with invalid JSON"""
        response = self.client.post(
            '/api/detect',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [400, 422])
    
    def test_detect_endpoint_no_content_type(self):
        """Test content detection without content type"""
        response = self.client.post(
            '/api/detect',
            data=json.dumps({'text': self.valid_text})
        )
        
        # Should handle missing content type
        self.assertIn(response.status_code, [400, 415, 422])
    
    def test_detect_endpoint_short_text(self):
        """Test content detection with very short text"""
        response = self.client.post(
            '/api/detect',
            json={'text': self.short_text},
            content_type='application/json'
        )
        
        # Should handle short text (may return warning but still process)
        self.assertIn(response.status_code, [200, 400])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('result', data)
    
    def test_detect_endpoint_long_text(self):
        """Test content detection with very long text"""
        long_text = "A" * 5000  # Very long text
        
        response = self.client.post(
            '/api/detect',
            json={'text': long_text},
            content_type='application/json'
        )
        
        # Should handle long text (may truncate but still process)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
    
    def test_file_upload_endpoint_valid_txt(self):
        """Test file upload with valid text file"""
        data = {
            'file': (io.BytesIO(self.sample_txt_content), 'test.txt', 'text/plain')
        }
        
        response = self.client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Should process text file successfully
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertIn('success', response_data)
        self.assertIn('result', response_data)
        self.assertTrue(response_data['success'])
    
    def test_file_upload_endpoint_valid_pdf(self):
        """Test file upload with PDF file"""
        data = {
            'file': (io.BytesIO(self.sample_pdf_content), 'test.pdf', 'application/pdf')
        }
        
        response = self.client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Should attempt to process PDF file
        # Note: May fail due to content parsing but should handle gracefully
        self.assertIn(response.status_code, [200, 400, 422])
    
    def test_file_upload_endpoint_no_file(self):
        """Test file upload without file"""
        response = self.client.post(
            '/api/upload',
            data={},
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_file_upload_endpoint_empty_file(self):
        """Test file upload with empty file"""
        data = {
            'file': (io.BytesIO(b''), 'empty.txt', 'text/plain')
        }
        
        response = self.client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_file_upload_endpoint_unsupported_type(self):
        """Test file upload with unsupported file type"""
        data = {
            'file': (io.BytesIO(b'fake image content'), 'test.jpg', 'image/jpeg')
        }
        
        response = self.client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Unsupported file type', data['error'])
    
    def test_file_upload_endpoint_large_file(self):
        """Test file upload with large file"""
        large_content = b"A" * (10 * 1024 * 1024)  # 10MB file
        data = {
            'file': (io.BytesIO(large_content), 'large.txt', 'text/plain')
        }
        
        response = self.client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Should handle large files (may reject or process)
        self.assertIn(response.status_code, [200, 400, 413, 422])
    
    @patch('routes.content_detection.detect_ai_content_enhanced')
    def test_detect_endpoint_with_mocked_detection(self, mock_detect):
        """Test content detection with mocked detection function"""
        # Mock the detection function to return predictable results
        mock_detect.return_value = {
            'ai_probability': 0.75,
            'human_probability': 0.25,
            'confidence': 0.85,
            'classification': 'Likely AI-Generated',
            'risk_level': 'High',
            'analysis': {},
            'feedback_messages': ['Test feedback'],
            'flagged_sections': [],
            'recommendations': []
        }
        
        response = self.client.post(
            '/api/detect',
            json={'text': self.valid_text},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify mock was called
        mock_detect.assert_called_once_with(self.valid_text)
        
        # Check response contains mocked data
        result = data['result']
        self.assertEqual(result['ai_probability'], 0.75)
        self.assertEqual(result['human_probability'], 0.25)
        self.assertEqual(result['confidence'], 0.85)
        self.assertEqual(result['classification'], 'Likely AI-Generated')
    
    @patch('routes.content_detection.detect_ai_content_enhanced')
    def test_detect_endpoint_detection_error(self, mock_detect):
        """Test content detection when detection function raises error"""
        # Mock the detection function to raise an exception
        mock_detect.side_effect = Exception("Detection error")
        
        response = self.client.post(
            '/api/detect',
            json={'text': self.valid_text},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options('/api/detect')
        
        # Should include CORS headers
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)
    
    def test_rate_limiting_simulation(self):
        """Test multiple rapid requests (simulating rate limiting)"""
        responses = []
        
        # Make multiple rapid requests
        for i in range(5):
            response = self.client.post(
                '/api/detect',
                json={'text': f'{self.valid_text} {i}'},
                content_type='application/json'
            )
            responses.append(response)
        
        # All requests should be processed (no rate limiting in test environment)
        for response in responses:
            self.assertEqual(response.status_code, 200)
    
    def test_concurrent_requests_simulation(self):
        """Test handling of concurrent-like requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = self.client.post(
                '/api/detect',
                json={'text': self.valid_text},
                content_type='application/json'
            )
            results.append(response.status_code)
        
        # Create multiple threads to simulate concurrent requests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        for status_code in results:
            self.assertEqual(status_code, 200)
    
    def test_endpoint_response_time(self):
        """Test endpoint response time"""
        import time
        
        start_time = time.time()
        response = self.client.post(
            '/api/detect',
            json={'text': self.valid_text},
            content_type='application/json'
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response should be reasonably fast (under 30 seconds)
        self.assertLess(response_time, 30.0)
        self.assertEqual(response.status_code, 200)
    
    def test_malformed_requests(self):
        """Test various malformed requests"""
        malformed_requests = [
            # Missing content type
            {'data': json.dumps({'text': self.valid_text}), 'content_type': None},
            # Wrong content type
            {'data': json.dumps({'text': self.valid_text}), 'content_type': 'text/plain'},
            # Invalid JSON structure
            {'json': {'invalid': 'structure'}, 'content_type': 'application/json'},
            # Null text
            {'json': {'text': None}, 'content_type': 'application/json'},
            # Non-string text
            {'json': {'text': 12345}, 'content_type': 'application/json'},
        ]
        
        for request_data in malformed_requests:
            response = self.client.post('/api/detect', **request_data)
            # Should handle malformed requests gracefully
            self.assertIn(response.status_code, [400, 415, 422, 500])


if __name__ == '__main__':
    unittest.main()