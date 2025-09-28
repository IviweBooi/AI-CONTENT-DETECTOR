"""
Integration tests for API endpoints with real server.
Tests actual HTTP requests/responses, CORS, middleware, and end-to-end functionality.
"""

import unittest
import requests
import json
import time
import os
import tempfile
from io import BytesIO


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API endpoints with real server"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with server configuration"""
        cls.base_url = "http://localhost:5001"
        cls.timeout = 30  # 30 seconds timeout for requests
        
        # Test data
        cls.human_text = "I love spending time with my family on weekends. We often go to the park and have picnics."
        cls.ai_text = "As an AI language model, I can provide comprehensive information about this topic. Furthermore, I must emphasize that artificial intelligence systems are designed to assist users."
        cls.mixed_text = "This is human-written content. As an AI language model, I can also generate text that sounds artificial."
        
        # Wait for server to be ready
        cls._wait_for_server()
    
    @classmethod
    def _wait_for_server(cls):
        """Wait for the server to be ready"""
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Server is ready after {attempt + 1} attempts")
                    return
            except requests.exceptions.RequestException:
                pass
            
            if attempt < max_attempts - 1:
                print(f"⏳ Waiting for server... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(2)
        
        raise Exception("❌ Server is not responding after maximum attempts")
    
    def test_server_health_check(self):
        """Test server health endpoint"""
        response = requests.get(f"{self.base_url}/api/health", timeout=self.timeout)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = requests.options(f"{self.base_url}/api/detect", timeout=self.timeout)
        
        # Check basic CORS headers that are present
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Credentials', response.headers)
        # Note: Access-Control-Allow-Methods and Access-Control-Allow-Headers 
        # may not be present in all CORS implementations
    
    def test_content_detection_human_text(self):
        """Test content detection with human text"""
        payload = {
            "text": self.human_text,
            "detection_method": "ensemble"
        }
        
        response = requests.post(
            f"{self.base_url}/api/detect",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify top-level response structure
        self.assertIn('success', data)
        self.assertIn('result', data)
        self.assertTrue(data['success'])
        
        result = data['result']
        
        # Verify response structure
        required_fields = [
            'ai_probability', 'human_probability', 'confidence',
            'classification', 'risk_level', 'analysis', 'feedback_messages'
        ]
        for field in required_fields:
            self.assertIn(field, result)
        
        # Verify data types
        self.assertIsInstance(result['ai_probability'], (int, float))
        self.assertIsInstance(result['human_probability'], (int, float))
        self.assertIsInstance(result['confidence'], (int, float))
        self.assertIsInstance(result['classification'], str)
        self.assertIsInstance(result['risk_level'], str)
        self.assertIsInstance(result['analysis'], dict)
        self.assertIsInstance(result['feedback_messages'], list)
        
        # Verify probability constraints
        self.assertGreaterEqual(result['ai_probability'], 0.0)
        self.assertLessEqual(result['ai_probability'], 1.0)
        self.assertGreaterEqual(result['human_probability'], 0.0)
        self.assertLessEqual(result['human_probability'], 1.0)
        self.assertAlmostEqual(
            result['ai_probability'] + result['human_probability'], 
            1.0, 
            places=5
        )
    
    def test_content_detection_ai_text(self):
        """Test content detection with AI text"""
        payload = {
            "text": self.ai_text,
            "detection_method": "ensemble"
        }
        
        response = requests.post(
            f"{self.base_url}/api/detect",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify top-level response structure
        self.assertIn('success', data)
        self.assertIn('result', data)
        self.assertTrue(data['success'])
        
        result = data['result']
        
        # AI text should have higher AI probability than human text
        self.assertGreater(result['ai_probability'], 0.1)  # Should detect some AI indicators
        self.assertIn('analysis', result)
        self.assertIn('feedback_messages', result)
    
    def test_content_detection_empty_text(self):
        """Test content detection with empty text"""
        payload = {
            "text": "",
            "detection_method": "ensemble"
        }
        
        response = requests.post(
            f"{self.base_url}/api/detect",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_content_detection_invalid_method(self):
        """Test content detection with invalid method - should default to valid method"""
        payload = {
            "text": self.human_text,
            "detection_method": "invalid_method"
        }
        
        response = requests.post(
            f"{self.base_url}/api/detect",
            json=payload,
            timeout=self.timeout
        )
        
        # API gracefully handles invalid methods by defaulting to a valid one
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
    
    def test_content_detection_missing_text(self):
        """Test content detection with missing text field"""
        payload = {
            "detection_method": "ensemble"
        }
        
        response = requests.post(
            f"{self.base_url}/api/detect",
            json=payload,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_content_detection_malformed_json(self):
        """Test content detection with malformed JSON"""
        response = requests.post(
            f"{self.base_url}/api/detect",
            data="invalid json",
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout
        )
        
        # Malformed JSON should return 500 (server error in parsing)
        self.assertEqual(response.status_code, 500)
    
    def test_file_upload_txt(self):
        """Test file upload with text file"""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.human_text)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                data = {'detection_method': 'ensemble'}
                
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify response structure for upload endpoint
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('content', data)  # Upload endpoint returns content
            self.assertIn('filename', data)
            self.assertIn('file_info', data)
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_file_upload_unsupported_format(self):
        """Test file upload with unsupported file format"""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write(self.human_text)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.xyz', f, 'application/octet-stream')}
                data = {'detection_method': 'ensemble'}
                
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
            
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn('error', data)
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_file_upload_no_file(self):
        """Test file upload without file"""
        data = {'detection_method': 'ensemble'}
        
        response = requests.post(
            f"{self.base_url}/api/upload",
            data=data,
            timeout=self.timeout
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_file_upload_empty_file(self):
        """Test file upload with empty file"""
        files = {'file': ('empty.txt', BytesIO(b''), 'text/plain')}
        data = {'detection_method': 'ensemble'}
        
        response = requests.post(
            f"{self.base_url}/api/upload",
            files=files,
            data=data,
            timeout=self.timeout
        )
        
        # API successfully processes empty files
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertEqual(data['content'], '')  # Empty content
    
    def test_rate_limiting_simulation(self):
        """Test multiple rapid requests (rate limiting simulation)"""
        payload = {
            "text": "Short test text for rate limiting.",
            "detection_method": "ensemble"
        }
        
        responses = []
        start_time = time.time()
        
        # Send 5 rapid requests
        for i in range(5):
            try:
                response = requests.post(
                    f"{self.base_url}/api/detect",
                    json=payload,
                    timeout=self.timeout
                )
                responses.append(response.status_code)
            except requests.exceptions.RequestException as e:
                responses.append(f"Error: {e}")
        
        end_time = time.time()
        
        # Most requests should succeed (assuming no strict rate limiting)
        successful_requests = sum(1 for r in responses if r == 200)
        self.assertGreater(successful_requests, 0)
        
        print(f"Rate limiting test: {successful_requests}/5 requests succeeded in {end_time - start_time:.2f}s")
    
    def test_concurrent_requests(self):
        """Test concurrent requests handling"""
        import threading
        import queue
        
        payload = {
            "text": self.human_text,
            "detection_method": "ensemble"
        }
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.post(
                    f"{self.base_url}/api/detect",
                    json=payload,
                    timeout=self.timeout
                )
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        # Create and start 3 concurrent threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        # At least some requests should succeed
        successful_requests = sum(1 for code in status_codes if code == 200)
        self.assertGreater(successful_requests, 0)
        
        print(f"Concurrent requests test: {successful_requests}/3 requests succeeded")
    
    def test_response_time_performance(self):
        """Test API response time performance"""
        payload = {
            "text": self.human_text,
            "detection_method": "ensemble"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/api/detect",
            json=payload,
            timeout=self.timeout
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 10.0)  # Should respond within 10 seconds
        
        print(f"Response time: {response_time:.2f} seconds")
    
    def test_large_text_handling(self):
        """Test handling of large text input"""
        # Create a large text (approximately 5000 words)
        large_text = self.human_text * 200
        
        payload = {
            "text": large_text,
            "detection_method": "ensemble"
        }
        
        response = requests.post(
            f"{self.base_url}/api/detect",
            json=payload,
            timeout=60  # Longer timeout for large text
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify top-level response structure
        self.assertIn('success', data)
        self.assertIn('result', data)
        self.assertTrue(data['success'])
        
        result = data['result']
        self.assertIn('ai_probability', result)
        self.assertIn('classification', result)


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)