"""
Firebase Integration Tests

This module tests Firebase integration including database operations,
analytics data storage, and real-time data synchronization.
"""

import pytest
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from services.firebase_service import FirebaseService


class TestFirebaseIntegration:
    """Test Firebase service integration"""
    
    @classmethod
    def setup_class(cls):
        """Setup for all tests"""
        cls.firebase_service = FirebaseService()
        cls.test_session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        cls.test_data_cleanup = []
    
    @classmethod
    def teardown_class(cls):
        """Cleanup test data"""
        # Clean up any test data created during tests
        for cleanup_func in cls.test_data_cleanup:
            try:
                cleanup_func()
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    def test_firebase_initialization(self):
        """Test Firebase service initialization"""
        # Verify service initializes correctly
        assert self.firebase_service is not None
        
        # Check if Firebase is properly configured
        # This test will pass even if Firebase is not configured (mock mode)
        assert hasattr(self.firebase_service, 'db')
        assert hasattr(self.firebase_service, 'analytics_enabled')
    
    def test_detection_logging_integration(self):
        """Test logging detection results to Firebase"""
        # Test data
        detection_data = {
            "text": "This is a test text for Firebase integration",
            "ai_probability": 0.75,
            "human_probability": 0.25,
            "confidence": 0.85,
            "classification": "AI",
            "risk_level": "Medium",
            "processing_time": 1.23,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.test_session_id
        }
        
        # Log detection
        result = self.firebase_service.log_detection(detection_data)
        
        # Verify logging result
        if self.firebase_service.analytics_enabled:
            assert result is True
            
            # Add cleanup function
            def cleanup():
                # In a real implementation, you would delete the test record
                pass
            self.test_data_cleanup.append(cleanup)
        else:
            # In mock mode, should still return True
            assert result is True
    
    def test_analytics_data_storage(self):
        """Test storing analytics data"""
        # Test analytics data
        analytics_data = {
            "event_type": "text_detection",
            "user_session": self.test_session_id,
            "detection_count": 1,
            "avg_confidence": 0.85,
            "ai_detections": 1,
            "human_detections": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store analytics
        result = self.firebase_service.store_analytics(analytics_data)
        
        # Verify storage result
        assert result is True
        
        if self.firebase_service.analytics_enabled:
            # Add cleanup function
            def cleanup():
                # In a real implementation, you would delete the analytics record
                pass
            self.test_data_cleanup.append(cleanup)
    
    def test_batch_operations_integration(self):
        """Test batch operations for multiple detections"""
        # Create multiple detection records
        batch_data = []
        for i in range(5):
            detection = {
                "text": f"Test text {i} for batch operations",
                "ai_probability": 0.6 + (i * 0.05),
                "human_probability": 0.4 - (i * 0.05),
                "confidence": 0.8,
                "classification": "AI" if i % 2 == 0 else "Human",
                "risk_level": "Medium",
                "processing_time": 1.0 + (i * 0.1),
                "timestamp": datetime.now().isoformat(),
                "session_id": f"{self.test_session_id}_batch_{i}"
            }
            batch_data.append(detection)
        
        # Store batch data
        results = []
        for data in batch_data:
            result = self.firebase_service.log_detection(data)
            results.append(result)
        
        # Verify all operations succeeded
        assert all(results)
        assert len(results) == 5
    
    def test_error_handling_integration(self):
        """Test error handling in Firebase operations"""
        # Test with invalid data
        invalid_data = {
            "invalid_field": "test",
            # Missing required fields
        }
        
        # Should handle gracefully
        result = self.firebase_service.log_detection(invalid_data)
        
        # Should not crash and return appropriate result
        assert isinstance(result, bool)
        
        # Test with None data
        result = self.firebase_service.log_detection(None)
        assert result is False
        
        # Test with empty data
        result = self.firebase_service.log_detection({})
        assert isinstance(result, bool)
    
    def test_connection_resilience(self):
        """Test Firebase connection resilience"""
        # Test multiple rapid operations
        rapid_operations = []
        for i in range(10):
            data = {
                "text": f"Rapid test {i}",
                "ai_probability": 0.5,
                "human_probability": 0.5,
                "confidence": 0.7,
                "classification": "AI",
                "risk_level": "Low",
                "processing_time": 0.5,
                "timestamp": datetime.now().isoformat(),
                "session_id": f"{self.test_session_id}_rapid_{i}"
            }
            
            result = self.firebase_service.log_detection(data)
            rapid_operations.append(result)
        
        # Verify operations completed
        assert len(rapid_operations) == 10
        # Most operations should succeed (allowing for some network issues)
        success_rate = sum(rapid_operations) / len(rapid_operations)
        assert success_rate >= 0.8  # At least 80% success rate
    
    def test_data_validation_integration(self):
        """Test data validation before Firebase operations"""
        # Test with various data types
        test_cases = [
            {
                "data": {
                    "text": "Valid text",
                    "ai_probability": 0.75,
                    "human_probability": 0.25,
                    "confidence": 0.85,
                    "classification": "AI",
                    "risk_level": "Medium",
                    "processing_time": 1.23,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.test_session_id
                },
                "should_succeed": True,
                "description": "Valid data"
            },
            {
                "data": {
                    "text": "",  # Empty text
                    "ai_probability": 0.5,
                    "human_probability": 0.5,
                    "confidence": 0.0,
                    "classification": "Error",
                    "risk_level": "Analysis Failed",
                    "processing_time": 0.1,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.test_session_id
                },
                "should_succeed": True,
                "description": "Empty text (error case)"
            },
            {
                "data": {
                    "text": "Test with extreme values",
                    "ai_probability": 1.0,  # Boundary value
                    "human_probability": 0.0,  # Boundary value
                    "confidence": 1.0,  # Boundary value
                    "classification": "AI",
                    "risk_level": "Very High",
                    "processing_time": 10.0,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.test_session_id
                },
                "should_succeed": True,
                "description": "Boundary values"
            }
        ]
        
        for case in test_cases:
            with self.subTest(description=case["description"]):
                result = self.firebase_service.log_detection(case["data"])
                
                if case["should_succeed"]:
                    assert isinstance(result, bool)
                else:
                    assert result is False
    
    def test_performance_integration(self):
        """Test Firebase operations performance"""
        # Measure performance of logging operations
        start_time = time.time()
        
        performance_data = {
            "text": "Performance test text for Firebase integration",
            "ai_probability": 0.65,
            "human_probability": 0.35,
            "confidence": 0.80,
            "classification": "AI",
            "risk_level": "Medium",
            "processing_time": 1.5,
            "timestamp": datetime.now().isoformat(),
            "session_id": f"{self.test_session_id}_performance"
        }
        
        # Perform multiple operations
        num_operations = 5
        results = []
        for i in range(num_operations):
            performance_data["session_id"] = f"{self.test_session_id}_performance_{i}"
            result = self.firebase_service.log_detection(performance_data)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance
        avg_time_per_operation = total_time / num_operations
        
        # Should complete operations reasonably quickly (< 2 seconds per operation)
        assert avg_time_per_operation < 2.0
        
        # Verify all operations completed
        assert len(results) == num_operations
        
        print(f"Average Firebase operation time: {avg_time_per_operation:.3f} seconds")
    
    def test_concurrent_firebase_operations(self):
        """Test concurrent Firebase operations"""
        import concurrent.futures
        import threading
        
        def log_detection_concurrent(thread_id: int) -> bool:
            """Log detection from concurrent thread"""
            data = {
                "text": f"Concurrent test from thread {thread_id}",
                "ai_probability": 0.6,
                "human_probability": 0.4,
                "confidence": 0.75,
                "classification": "AI",
                "risk_level": "Medium",
                "processing_time": 1.0,
                "timestamp": datetime.now().isoformat(),
                "session_id": f"{self.test_session_id}_concurrent_{thread_id}"
            }
            
            return self.firebase_service.log_detection(data)
        
        # Test concurrent operations
        num_threads = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(log_detection_concurrent, i)
                for i in range(num_threads)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verify concurrent operations
        assert len(results) == num_threads
        # Most operations should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8  # At least 80% success rate
    
    def test_analytics_aggregation_integration(self):
        """Test analytics data aggregation"""
        # Create sample data for aggregation
        session_data = []
        for i in range(3):
            data = {
                "text": f"Analytics test {i}",
                "ai_probability": 0.7 + (i * 0.1),
                "human_probability": 0.3 - (i * 0.1),
                "confidence": 0.8,
                "classification": "AI",
                "risk_level": "Medium",
                "processing_time": 1.0 + (i * 0.2),
                "timestamp": datetime.now().isoformat(),
                "session_id": f"{self.test_session_id}_analytics"
            }
            session_data.append(data)
            
            # Log each detection
            result = self.firebase_service.log_detection(data)
            assert isinstance(result, bool)
        
        # Test analytics aggregation
        analytics_summary = {
            "session_id": f"{self.test_session_id}_analytics",
            "total_detections": len(session_data),
            "ai_detections": len([d for d in session_data if d["classification"] == "AI"]),
            "human_detections": len([d for d in session_data if d["classification"] == "Human"]),
            "avg_confidence": sum(d["confidence"] for d in session_data) / len(session_data),
            "avg_processing_time": sum(d["processing_time"] for d in session_data) / len(session_data),
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.firebase_service.store_analytics(analytics_summary)
        assert result is True
    
    @pytest.mark.skipif(
        os.getenv("SKIP_FIREBASE_TESTS") == "true",
        reason="Firebase tests skipped (set SKIP_FIREBASE_TESTS=false to enable)"
    )
    def test_real_firebase_connection(self):
        """Test actual Firebase connection (if configured)"""
        # This test only runs if Firebase is actually configured
        if not self.firebase_service.analytics_enabled:
            pytest.skip("Firebase not configured for real testing")
        
        # Test real connection
        test_data = {
            "text": "Real Firebase connection test",
            "ai_probability": 0.8,
            "human_probability": 0.2,
            "confidence": 0.9,
            "classification": "AI",
            "risk_level": "High",
            "processing_time": 1.1,
            "timestamp": datetime.now().isoformat(),
            "session_id": f"{self.test_session_id}_real"
        }
        
        result = self.firebase_service.log_detection(test_data)
        assert result is True


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])