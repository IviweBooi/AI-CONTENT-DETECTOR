"""
Ensemble Detector Integration Tests

This module tests the ensemble detector with real models and components,
ensuring proper integration between neural networks, pattern detection,
and confidence tuning systems.
"""

import pytest
import os
import sys
import tempfile
import time
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from utils.ensemble_detector import EnsembleAIDetector
from predictor_model.cnn_text_classifier import CNNTextClassifier
from utils.pattern_detector import PatternDetector


class TestEnsembleIntegration:
    """Test ensemble detector integration with real components"""
    
    @classmethod
    def setup_class(cls):
        """Setup for all tests"""
        cls.ensemble = EnsembleAIDetector()
        cls.cnn_classifier = CNNTextClassifier()
        cls.pattern_detector = PatternDetector()
    
    def test_ensemble_initialization(self):
        """Test that ensemble detector initializes all components correctly"""
        # Verify ensemble has required components
        assert hasattr(self.ensemble, 'cnn_classifier')
        assert hasattr(self.ensemble, 'pattern_detector')
        assert hasattr(self.ensemble, 'weights')
        
        # Verify weights are properly configured
        assert 'cnn' in self.ensemble.weights
        assert 'pattern' in self.ensemble.weights
        assert abs(sum(self.ensemble.weights.values()) - 1.0) < 0.01
    
    def test_neural_pattern_integration(self):
        """Test integration between neural and pattern detection"""
        test_cases = [
            {
                "text": "As an AI language model, I can provide comprehensive analysis of this topic with detailed explanations.",
                "expected_classification": "AI",
                "description": "Strong AI indicators"
            },
            {
                "text": "I personally think this movie was amazing! The characters felt so real and the plot kept me engaged throughout.",
                "expected_classification": "Human",
                "description": "Strong human indicators"
            },
            {
                "text": "The weather today is sunny with a temperature of 25 degrees Celsius.",
                "expected_classification": "Analysis Pending",
                "description": "Neutral content"
            }
        ]
        
        for case in test_cases:
            with self.subTest(description=case["description"]):
                # Get individual component predictions
                cnn_result = self.cnn_classifier.predict(case["text"])
                pattern_result = self.pattern_detector.analyze_text(case["text"])
                
                # Get ensemble prediction
                ensemble_result = self.ensemble.detect(case["text"])
                
                # Verify ensemble combines both components
                assert "ai_probability" in ensemble_result
                assert "human_probability" in ensemble_result
                assert "confidence" in ensemble_result
                assert "classification" in ensemble_result
                
                # Verify classification matches expected
                if case["expected_classification"] != "Analysis Pending":
                    assert ensemble_result["classification"] == case["expected_classification"]
                
                # Verify probability consistency
                if ensemble_result["classification"] in ["Human", "AI"]:
                    prob_sum = ensemble_result["ai_probability"] + ensemble_result["human_probability"]
                    assert abs(prob_sum - 1.0) < 0.01
    
    def test_confidence_tuning_integration(self):
        """Test confidence tuning based on component agreement"""
        # Test case where components should agree (high confidence)
        ai_text = "As an AI assistant, I can help you with this task. Here are the steps: 1) First step 2) Second step 3) Final step."
        result = self.ensemble.detect(ai_text)
        
        # Should have high confidence when components agree
        assert result["confidence"] > 0.6
        assert result["classification"] == "AI"
        
        # Test case where components might disagree (lower confidence)
        ambiguous_text = "This is a simple statement about the weather."
        result = self.ensemble.detect(ambiguous_text)
        
        # Confidence should reflect uncertainty
        assert 0 <= result["confidence"] <= 1
    
    def test_weight_application_integration(self):
        """Test that ensemble weights are properly applied"""
        test_text = "As an AI language model, I can provide detailed information about this topic."
        
        # Get individual predictions
        cnn_result = self.cnn_classifier.predict(test_text)
        pattern_result = self.pattern_detector.analyze_text(test_text)
        
        # Get ensemble prediction
        ensemble_result = self.ensemble.detect(test_text)
        
        # Verify ensemble result is influenced by both components
        # The exact calculation depends on the weighting scheme
        assert ensemble_result["ai_probability"] >= 0
        assert ensemble_result["human_probability"] >= 0
        
        # Verify the result is reasonable given the inputs
        if cnn_result["ai_probability"] > 0.7 and pattern_result.get("ai_probability", 0) > 0.7:
            assert ensemble_result["ai_probability"] > 0.5
    
    def test_error_propagation_integration(self):
        """Test how errors propagate through the ensemble"""
        # Test with empty text
        result = self.ensemble.detect("")
        assert result["classification"] == "Error"
        assert result["risk_level"] == "Analysis Failed"
        
        # Test with very short text
        result = self.ensemble.detect("Hi")
        assert result["classification"] == "Analysis Pending"
        
        # Test with None input
        result = self.ensemble.detect(None)
        assert result["classification"] == "Error"
    
    def test_performance_integration(self):
        """Test performance of integrated ensemble system"""
        test_texts = [
            "This is a test of the ensemble system performance.",
            "As an AI, I can process this text quickly and efficiently.",
            "Human-written content with personal opinions and experiences.",
            "Technical documentation with specific implementation details.",
            "Creative writing with emotional depth and narrative flow."
        ]
        
        start_time = time.time()
        results = []
        
        for text in test_texts:
            result = self.ensemble.detect(text)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all results are valid
        assert len(results) == len(test_texts)
        for result in results:
            assert "classification" in result
            assert "confidence" in result
            assert result["classification"] in ["Human", "AI", "Analysis Pending", "Error"]
        
        # Verify reasonable performance (should process 5 texts in under 10 seconds)
        assert total_time < 10.0
        
        # Calculate average processing time
        avg_time = total_time / len(test_texts)
        print(f"Average processing time per text: {avg_time:.3f} seconds")
    
    def test_model_fallback_integration(self):
        """Test fallback behavior when models are unavailable"""
        # Test CNN fallback to rule-based
        with patch.object(self.ensemble.cnn_classifier, 'model', None):
            result = self.ensemble.detect("As an AI language model, I can help you.")
            
            # Should still work with rule-based fallback
            assert "classification" in result
            assert result["classification"] in ["Human", "AI", "Analysis Pending"]
        
        # Test pattern detector fallback
        with patch.object(self.ensemble.pattern_detector, 'ai_patterns', []):
            result = self.ensemble.detect("This is test text for pattern fallback.")
            
            # Should still work even with limited patterns
            assert "classification" in result
    
    def test_memory_usage_integration(self):
        """Test memory usage during ensemble processing"""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple texts
        large_texts = [
            "This is a large text sample. " * 100 + f"Text number {i}"
            for i in range(10)
        ]
        
        results = []
        for text in large_texts:
            result = self.ensemble.detect(text)
            results.append(result)
        
        # Force garbage collection
        gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify reasonable memory usage (should not increase by more than 100MB)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.2f} MB"
        
        # Verify all results are valid
        assert len(results) == len(large_texts)
        for result in results:
            assert "classification" in result
    
    def test_concurrent_processing_integration(self):
        """Test ensemble detector under concurrent load"""
        import concurrent.futures
        import threading
        
        def process_text(text_id: int) -> dict:
            """Process text with unique identifier"""
            text = f"This is test text number {text_id} for concurrent processing."
            return self.ensemble.detect(text)
        
        # Test concurrent processing
        num_threads = 5
        num_requests = 20
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(process_text, i)
                for i in range(num_requests)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verify all requests completed successfully
        assert len(results) == num_requests
        for result in results:
            assert "classification" in result
            assert "confidence" in result
            assert result["classification"] in ["Human", "AI", "Analysis Pending", "Error"]
    
    def test_edge_cases_integration(self):
        """Test ensemble behavior with edge cases"""
        edge_cases = [
            {"text": "", "description": "Empty string"},
            {"text": "   ", "description": "Whitespace only"},
            {"text": "a", "description": "Single character"},
            {"text": "123456789", "description": "Numbers only"},
            {"text": "!@#$%^&*()", "description": "Special characters only"},
            {"text": "A" * 10000, "description": "Very long repetitive text"},
            {"text": "Hello\n\nWorld\n\n\nTest", "description": "Multiple newlines"},
            {"text": "Mixed 123 content !@# with various elements", "description": "Mixed content"}
        ]
        
        for case in edge_cases:
            with self.subTest(description=case["description"]):
                result = self.ensemble.detect(case["text"])
                
                # Verify result structure
                assert isinstance(result, dict)
                assert "classification" in result
                assert "confidence" in result
                assert "ai_probability" in result
                assert "human_probability" in result
                
                # Verify valid classification
                assert result["classification"] in ["Human", "AI", "Analysis Pending", "Error"]
                
                # Verify probability bounds
                assert 0 <= result["ai_probability"] <= 1
                assert 0 <= result["human_probability"] <= 1
                assert 0 <= result["confidence"] <= 1


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])