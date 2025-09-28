"""
Cross-Component Integration Tests

This module tests the integration and interaction between different components
of the AI Content Detector system, including neural networks, pattern detection,
confidence tuning, and their combined decision-making processes.
"""

import pytest
import os
import sys
import time
import numpy as np
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from utils.ensemble_detector import EnsembleAIDetector
from predictor_model.cnn_text_classifier import CNNTextClassifier
from utils.pattern_detector import PatternDetector
from services.firebase_service import FirebaseService


class TestCrossComponentIntegration:
    """Test cross-component integration and interactions"""
    
    @classmethod
    def setup_class(cls):
        """Setup for all tests"""
        cls.ensemble = EnsembleAIDetector()
        cls.cnn_classifier = CNNTextClassifier()
        cls.pattern_detector = PatternDetector()
        cls.firebase_service = FirebaseService()
    
    def test_neural_pattern_confidence_integration(self):
        """Test integration between neural network, pattern detection, and confidence tuning"""
        test_cases = [
            {
                "text": "As an AI language model, I can provide comprehensive analysis with detailed explanations and structured responses.",
                "expected_high_confidence": True,
                "expected_classification": "AI",
                "description": "Strong AI indicators across all components"
            },
            {
                "text": "I personally love this movie! It made me cry and laugh at the same time. The characters felt so real to me.",
                "expected_high_confidence": True,
                "expected_classification": "Human",
                "description": "Strong human indicators across all components"
            },
            {
                "text": "The weather is nice today.",
                "expected_high_confidence": False,
                "expected_classification": "Analysis Pending",
                "description": "Ambiguous content with low confidence"
            }
        ]
        
        for case in test_cases:
            with self.subTest(description=case["description"]):
                # Get individual component results
                cnn_result = self.cnn_classifier.predict(case["text"])
                pattern_result = self.pattern_detector.analyze_text(case["text"])
                ensemble_result = self.ensemble.detect(case["text"])
                
                # Test component agreement
                if case["expected_high_confidence"]:
                    # Components should agree on classification
                    if ensemble_result["classification"] == "AI":
                        assert cnn_result["ai_probability"] > 0.5
                        assert pattern_result.get("ai_probability", 0.5) >= 0.5
                    elif ensemble_result["classification"] == "Human":
                        assert cnn_result["human_probability"] > 0.5
                        assert pattern_result.get("human_probability", 0.5) >= 0.5
                    
                    # Ensemble confidence should be high when components agree
                    assert ensemble_result["confidence"] > 0.6
                
                # Test confidence tuning based on agreement
                cnn_confidence = cnn_result.get("confidence", 0.5)
                pattern_confidence = pattern_result.get("confidence", 0.5)
                ensemble_confidence = ensemble_result["confidence"]
                
                # Ensemble confidence should reflect component agreement
                if abs(cnn_confidence - pattern_confidence) < 0.2:
                    # Components agree - confidence should be higher
                    assert ensemble_confidence >= min(cnn_confidence, pattern_confidence)
    
    def test_weight_adjustment_integration(self):
        """Test dynamic weight adjustment based on component performance"""
        # Test texts where different components should excel
        neural_strong_text = "As an AI assistant, I can help you with various tasks including data analysis, content generation, and problem-solving."
        pattern_strong_text = "I can assist you with this task. Here are the steps: 1) First step 2) Second step 3) Final step."
        
        # Get results for neural-strong text
        neural_result = self.ensemble.detect(neural_strong_text)
        
        # Get results for pattern-strong text
        pattern_result = self.ensemble.detect(pattern_strong_text)
        
        # Both should be classified as AI but potentially with different confidence levels
        assert neural_result["classification"] == "AI"
        assert pattern_result["classification"] == "AI"
        
        # Verify that the ensemble is using both components effectively
        assert neural_result["ai_probability"] > 0.6
        assert pattern_result["ai_probability"] > 0.6
    
    def test_fallback_mechanism_integration(self):
        """Test fallback mechanisms when components fail"""
        test_text = "This is a test of the fallback mechanism integration."
        
        # Test CNN fallback to rule-based
        with patch.object(self.ensemble.cnn_classifier, 'model', None):
            result_cnn_fallback = self.ensemble.detect(test_text)
            
            # Should still work with pattern detector + rule-based CNN
            assert "classification" in result_cnn_fallback
            assert result_cnn_fallback["classification"] in ["Human", "AI", "Analysis Pending"]
        
        # Test pattern detector with limited patterns
        with patch.object(self.ensemble.pattern_detector, 'ai_patterns', ["AI assistant"]):
            result_pattern_limited = self.ensemble.detect(test_text)
            
            # Should still work with CNN + limited patterns
            assert "classification" in result_pattern_limited
            assert result_pattern_limited["classification"] in ["Human", "AI", "Analysis Pending"]
        
        # Test both components with limitations
        with patch.object(self.ensemble.cnn_classifier, 'model', None), \
             patch.object(self.ensemble.pattern_detector, 'ai_patterns', []):
            result_both_limited = self.ensemble.detect(test_text)
            
            # Should still provide some result
            assert "classification" in result_both_limited
    
    def test_confidence_calibration_integration(self):
        """Test confidence calibration across components"""
        # Test with various confidence scenarios
        confidence_tests = [
            {
                "text": "As an AI language model trained on diverse datasets, I can provide comprehensive analysis.",
                "expected_min_confidence": 0.8,
                "description": "Very clear AI text"
            },
            {
                "text": "I absolutely love this book! It changed my perspective on life completely.",
                "expected_min_confidence": 0.7,
                "description": "Very clear human text"
            },
            {
                "text": "The process involves several steps that need to be followed carefully.",
                "expected_max_confidence": 0.6,
                "description": "Ambiguous technical text"
            }
        ]
        
        for test in confidence_tests:
            with self.subTest(description=test["description"]):
                result = self.ensemble.detect(test["text"])
                
                if "expected_min_confidence" in test:
                    assert result["confidence"] >= test["expected_min_confidence"]
                elif "expected_max_confidence" in test:
                    assert result["confidence"] <= test["expected_max_confidence"]
                
                # Verify confidence is properly calibrated (0-1 range)
                assert 0 <= result["confidence"] <= 1
    
    def test_error_propagation_integration(self):
        """Test how errors propagate through the component chain"""
        error_cases = [
            {"text": "", "expected_classification": "Error"},
            {"text": None, "expected_classification": "Error"},
            {"text": "   ", "expected_classification": "Error"},
            {"text": "Hi", "expected_classification": "Analysis Pending"}
        ]
        
        for case in error_cases:
            with self.subTest(text=case["text"]):
                # Test individual components
                try:
                    cnn_result = self.cnn_classifier.predict(case["text"])
                    pattern_result = self.pattern_detector.analyze_text(case["text"])
                    ensemble_result = self.ensemble.detect(case["text"])
                    
                    # Ensemble should handle errors gracefully
                    assert ensemble_result["classification"] == case["expected_classification"]
                    
                    # Error responses should have consistent structure
                    if case["expected_classification"] == "Error":
                        assert ensemble_result["risk_level"] == "Analysis Failed"
                        assert ensemble_result["ai_probability"] == 0.0
                        assert ensemble_result["human_probability"] == 0.0
                
                except Exception as e:
                    # Components should not crash on invalid input
                    pytest.fail(f"Component crashed on input {case['text']}: {e}")
    
    def test_performance_optimization_integration(self):
        """Test performance optimization across components"""
        # Test with various text lengths
        performance_tests = [
            {"text": "Short text", "max_time": 2.0},
            {"text": "Medium length text " * 10, "max_time": 3.0},
            {"text": "Long text " * 100, "max_time": 5.0}
        ]
        
        for test in performance_tests:
            with self.subTest(length=len(test["text"])):
                start_time = time.time()
                
                # Run detection
                result = self.ensemble.detect(test["text"])
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Verify performance
                assert processing_time < test["max_time"]
                assert "classification" in result
                
                print(f"Text length {len(test['text'])}: {processing_time:.3f}s")
    
    def test_memory_efficiency_integration(self):
        """Test memory efficiency across components"""
        import psutil
        import gc
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple texts
        test_texts = [
            f"This is test text number {i} for memory efficiency testing. " * 20
            for i in range(20)
        ]
        
        results = []
        for text in test_texts:
            result = self.ensemble.detect(text)
            results.append(result)
        
        # Force garbage collection
        gc.collect()
        
        # Check final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify reasonable memory usage
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f} MB"
        assert len(results) == len(test_texts)
    
    def test_concurrent_component_access(self):
        """Test concurrent access to components"""
        import concurrent.futures
        import threading
        
        def process_concurrent_text(thread_id: int) -> dict:
            """Process text in concurrent thread"""
            text = f"Concurrent processing test {thread_id} with various components working together."
            return self.ensemble.detect(text)
        
        # Test concurrent processing
        num_threads = 8
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(process_concurrent_text, i)
                for i in range(num_threads)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verify all threads completed successfully
        assert len(results) == num_threads
        for result in results:
            assert "classification" in result
            assert "confidence" in result
    
    def test_data_flow_integration(self):
        """Test data flow between components"""
        test_text = "As an AI assistant, I can help you with comprehensive analysis and detailed explanations."
        
        # Trace data flow through components
        # Step 1: CNN processing
        cnn_result = self.cnn_classifier.predict(test_text)
        assert "ai_probability" in cnn_result
        assert "confidence" in cnn_result
        
        # Step 2: Pattern detection
        pattern_result = self.pattern_detector.analyze_text(test_text)
        assert isinstance(pattern_result, dict)
        
        # Step 3: Ensemble combination
        ensemble_result = self.ensemble.detect(test_text)
        
        # Verify data flow consistency
        assert ensemble_result["classification"] in ["Human", "AI", "Analysis Pending", "Error"]
        
        # Verify ensemble incorporates both components
        if cnn_result["ai_probability"] > 0.7 and pattern_result.get("ai_probability", 0) > 0.7:
            assert ensemble_result["ai_probability"] > 0.6
    
    def test_component_state_consistency(self):
        """Test state consistency across components"""
        # Process same text multiple times
        test_text = "This is a consistency test for component state management."
        
        results = []
        for i in range(5):
            result = self.ensemble.detect(test_text)
            results.append(result)
        
        # Verify consistent results
        first_result = results[0]
        for result in results[1:]:
            assert result["classification"] == first_result["classification"]
            assert abs(result["ai_probability"] - first_result["ai_probability"]) < 0.01
            assert abs(result["confidence"] - first_result["confidence"]) < 0.01
    
    def test_integration_with_analytics(self):
        """Test integration with analytics and logging"""
        test_text = "Integration test with analytics and logging components."
        
        # Get detection result
        result = self.ensemble.detect(test_text)
        
        # Prepare analytics data
        analytics_data = {
            "text": test_text,
            "ai_probability": result["ai_probability"],
            "human_probability": result["human_probability"],
            "confidence": result["confidence"],
            "classification": result["classification"],
            "risk_level": result["risk_level"],
            "processing_time": 1.0,
            "timestamp": time.time(),
            "session_id": "integration_test"
        }
        
        # Test Firebase integration
        firebase_result = self.firebase_service.log_detection(analytics_data)
        assert isinstance(firebase_result, bool)
        
        # Test analytics storage
        analytics_summary = {
            "session_id": "integration_test",
            "total_detections": 1,
            "ai_detections": 1 if result["classification"] == "AI" else 0,
            "human_detections": 1 if result["classification"] == "Human" else 0,
            "avg_confidence": result["confidence"],
            "timestamp": time.time()
        }
        
        analytics_result = self.firebase_service.store_analytics(analytics_summary)
        assert isinstance(analytics_result, bool)


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])