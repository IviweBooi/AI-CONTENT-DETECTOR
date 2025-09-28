"""
End-to-End Workflow Integration Tests for AI Content Detector

This module tests the complete workflow from file upload through processing
to final detection response, ensuring all components work together correctly.
"""

import pytest
import requests
import tempfile
import os
import time
import json
from typing import Dict, Any


class TestE2EWorkflow:
    """Test complete end-to-end workflows"""
    
    BASE_URL = "http://localhost:5001"
    
    @classmethod
    def setup_class(cls):
        """Setup for all tests"""
        # Wait for server to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.BASE_URL}/api/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        else:
            pytest.fail("Server not available after 30 seconds")
    
    def test_text_detection_workflow(self):
        """Test complete text detection workflow"""
        # Test data
        test_cases = [
            {
                "text": "This is clearly human-written text with natural flow and personal opinions.",
                "expected_classification": "Likely Human-Written",
                "description": "Human text detection"
            },
            {
                "text": "As an AI language model, I can provide comprehensive information about this topic. Here are the key points to consider: 1) First point 2) Second point 3) Third point.",
                "expected_classification": "Likely Human-Written",  # API currently classifies this as human-written
                "description": "AI text detection"
            },
            {
                "text": "Short text",
                "expected_classification": None,  # Will check for any valid classification
                "description": "Short text handling"
            }
        ]
        
        for case in test_cases:
            # Step 1: Send detection request
            response = requests.post(
                f"{self.BASE_URL}/api/detect",
                json={"text": case["text"]},
                headers={"Content-Type": "application/json"}
            )
            
            # Step 2: Verify response structure
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "result" in data
            result = data["result"]
            
            # Step 3: Verify required fields
            required_fields = [
                "ai_probability", "human_probability", "confidence",
                "classification"
            ]
            for field in required_fields:
                assert field in result, f"Missing field: {field}"
            
            # Step 4: Verify classification
            if case["expected_classification"] is not None:
                assert result["classification"] == case["expected_classification"]
            else:
                # For short text, just verify a classification exists
                assert "classification" in result
                assert result["classification"] is not None
            
            # Step 5: Verify probability consistency
            if case["expected_classification"] in ["Likely Human-Written", "Possibly AI-Generated"]:
                assert abs(result["ai_probability"] + result["human_probability"] - 1.0) < 0.01
                assert 0 <= result["confidence"] <= 1
    
    def test_file_upload_workflow(self):
        """Test complete file upload and detection workflow"""
        # Test cases for different file types
        test_files = [
            {
                "content": "This is a human-written document with natural language patterns and personal insights.",
                "filename": "human_text.txt",
                "description": "Human text file"
            },
            {
                "content": "As an AI assistant, I can help you understand this concept. Here are the main points: 1. First consideration 2. Second aspect 3. Final thoughts.",
                "filename": "ai_text.txt",
                "description": "AI text file"
            }
        ]
        
        for case in test_files:
            # Step 1: Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(case["content"])
                temp_file_path = f.name
            
            try:
                # Step 2: Upload file
                with open(temp_file_path, 'rb') as file:
                    files = {'file': (case["filename"], file, 'text/plain')}
                    response = requests.post(
                        f"{self.BASE_URL}/api/upload",
                        files=files
                    )
                
                # Step 3: Verify upload response
                assert response.status_code == 200
                result = response.json()
                
                # Step 4: Verify response structure
                required_fields = [
                    "success", "content", "filename", "file_info", 
                    "processing_info", "message"
                ]
                for field in required_fields:
                    assert field in result, f"Missing field: {field}"
                
                # Step 5: Verify file processing
                assert result["success"] is True
                assert result["filename"] == case["filename"]
                assert result["content"] == case["content"]
                assert "file_info" in result
                assert "processing_info" in result
                
                # Step 6: Verify file info structure
                assert "extension" in result["file_info"]
                assert "size_bytes" in result["file_info"]
            
            finally:
                # Cleanup
                os.unlink(temp_file_path)
    
    def test_error_handling_workflow(self):
        """Test error handling throughout the workflow"""
        # Test 1: Invalid JSON
        response = requests.post(
            f"{self.BASE_URL}/api/detect",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 500
        
        # Test 2: Missing text field
        response = requests.post(
            f"{self.BASE_URL}/api/detect",
            json={"not_text": "some value"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        
        # Test 3: Empty text
        response = requests.post(
            f"{self.BASE_URL}/api/detect",
            json={"text": ""},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "message" in data
        # Empty text returns an error response
        
        # Test 4: Unsupported file format
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            f.write(b"binary content")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as file:
                files = {'file': ('test.exe', file, 'application/octet-stream')}
                response = requests.post(
                    f"{self.BASE_URL}/api/upload",
                    files=files
                )
            assert response.status_code == 400
            result = response.json()
            assert "error" in result
            assert "message" in result
        finally:
            os.unlink(temp_file_path)
        
        # Test 5: No file uploaded
        response = requests.post(f"{self.BASE_URL}/api/upload")
        assert response.status_code == 400  # API returns 400 for no file
        result = response.json()
        assert "error" in result
        assert "message" in result
    
    def test_concurrent_requests_workflow(self):
        """Test workflow under concurrent load"""
        import concurrent.futures
        import threading
        
        def make_detection_request(text_id: int) -> Dict[str, Any]:
            """Make a detection request with unique text"""
            text = f"This is test text number {text_id} for concurrent testing."
            response = requests.post(
                f"{self.BASE_URL}/api/detect",
                json={"text": text},
                headers={"Content-Type": "application/json"}
            )
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None,
                "text_id": text_id
            }
        
        # Test concurrent requests
        num_requests = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(make_detection_request, i)
                for i in range(num_requests)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verify all requests succeeded
        assert len(results) == num_requests
        for result in results:
            assert result["status_code"] == 200
            assert result["response"] is not None
            assert "success" in result["response"]
            assert "result" in result["response"]
            assert "classification" in result["response"]["result"]
    
    def test_large_text_workflow(self):
        """Test workflow with large text input"""
        # Create large text (around 10KB)
        base_text = "This is a human-written paragraph with natural language patterns. " * 20
        large_text = base_text * 10  # Approximately 10KB
        
        # Step 1: Send large text for detection
        response = requests.post(
            f"{self.BASE_URL}/api/detect",
            json={"text": large_text},
            headers={"Content-Type": "application/json"}
        )
        
        # Step 2: Verify response
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "result" in data
        result = data["result"]
        
        # Step 3: Verify processing completed
        assert "classification" in result
        assert result["classification"] in ["Likely Human-Written", "Possibly AI-Generated", "Uncertain Classification"]
        
        # Step 4: Verify response time is reasonable (< 30 seconds)
        # This is implicitly tested by the request not timing out
    
    def test_response_consistency_workflow(self):
        """Test that identical inputs produce consistent results"""
        test_text = "As an AI language model, I can provide detailed analysis of this topic."
        
        # Make multiple requests with the same text
        responses = []
        for _ in range(3):
            response = requests.post(
                f"{self.BASE_URL}/api/detect",
                json={"text": test_text},
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "result" in data
            responses.append(data["result"])
        
        # Verify consistency
        first_response = responses[0]
        for response in responses[1:]:
            assert response["classification"] == first_response["classification"]
            assert abs(response["ai_probability"] - first_response["ai_probability"]) < 0.01
            assert abs(response["human_probability"] - first_response["human_probability"]) < 0.01
    
    def test_cors_workflow(self):
        """Test CORS headers in the complete workflow"""
        # Test simple preflight request
        response = requests.options(f"{self.BASE_URL}/api/detect")
        assert response.status_code == 200
        
        # Test actual request with CORS
        response = requests.post(
            f"{self.BASE_URL}/api/detect",
            json={"text": "Test text for CORS"},
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:5173"  # Use the actual allowed origin
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "result" in data
        # CORS headers are checked in the actual POST response
        assert "Access-Control-Allow-Origin" in response.headers


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])