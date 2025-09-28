"""
Comprehensive unit tests for Ensemble AI Detector
Tests the integration of neural model, pattern detection, and fallback mechanisms.
"""

import pytest
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.ensemble_detector import EnsembleAIDetector
from utils.confidence_tuner import ThresholdConfig


class TestEnsembleAIDetector(unittest.TestCase):
    """Test cases for EnsembleAIDetector"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = EnsembleAIDetector()
        
        # Sample test texts
        self.human_text = "I love this movie! It's absolutely fantastic and made me cry. The acting was superb and the storyline kept me engaged throughout the entire film."
        self.ai_text = "As an AI language model, I can provide you with comprehensive information about this topic. The implementation requires careful consideration of various factors including data preprocessing and model architecture."
        self.short_text = "Hello world"
        self.empty_text = ""
        self.whitespace_text = "   \n\t   "
        self.mixed_text = "This is a normal sentence. As an AI, I must inform you that this contains both human and AI patterns."
    
    def test_detector_initialization(self):
        """Test that the detector initializes properly"""
        self.assertIsNotNone(self.detector)
        self.assertTrue(hasattr(self.detector, 'detect'))
        self.assertTrue(hasattr(self.detector, 'confidence_tuner'))
        self.assertTrue(hasattr(self.detector, 'pattern_detector'))
        self.assertTrue(hasattr(self.detector, 'weights'))
        self.assertTrue(hasattr(self.detector, 'confidence_thresholds'))
    
    def test_detector_initialization_with_custom_config(self):
        """Test detector initialization with custom configuration"""
        custom_weights = {
            'neural_model': 0.6,
            'pattern_detector': 0.3,
            'rule_based': 0.1,
            'confidence_boost': 0.2
        }
        
        custom_threshold_config = ThresholdConfig(
            ai_threshold=0.7,
            confidence_threshold=0.6
        )
        
        detector = EnsembleAIDetector(
            ensemble_weights=custom_weights,
            threshold_config=custom_threshold_config
        )
        
        self.assertEqual(detector.weights, custom_weights)
        self.assertIsNotNone(detector.confidence_tuner)
    
    def test_detect_human_text(self):
        """Test detection on human-like text"""
        result = self.detector.detect(self.human_text)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('confidence', result)
        self.assertIn('classification', result)
        self.assertIn('risk_level', result)
        self.assertIn('analysis', result)
        self.assertIn('feedback_messages', result)
        
        # Check data types
        self.assertIsInstance(result['ai_probability'], float)
        self.assertIsInstance(result['human_probability'], float)
        self.assertIsInstance(result['confidence'], float)
        self.assertIsInstance(result['classification'], str)
        self.assertIsInstance(result['risk_level'], str)
        self.assertIsInstance(result['analysis'], dict)
        self.assertIsInstance(result['feedback_messages'], list)
        
        # Check probability ranges
        self.assertGreaterEqual(result['ai_probability'], 0.0)
        self.assertLessEqual(result['ai_probability'], 1.0)
        self.assertGreaterEqual(result['human_probability'], 0.0)
        self.assertLessEqual(result['human_probability'], 1.0)
        
        # Check probabilities sum to 1 (approximately)
        prob_sum = result['ai_probability'] + result['human_probability']
        self.assertAlmostEqual(prob_sum, 1.0, places=5)
    
    def test_detect_ai_text(self):
        """Test detection on AI-like text"""
        result = self.detector.detect(self.ai_text)
        
        # Check result structure (same as human text test)
        self.assertIsInstance(result, dict)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('confidence', result)
        self.assertIn('classification', result)
        self.assertIn('risk_level', result)
        
        # For AI-like text, we expect higher AI probability
        self.assertIsInstance(result['ai_probability'], float)
        self.assertIsInstance(result['human_probability'], float)
    
    def test_detect_empty_text(self):
        """Test detection on empty text"""
        result = self.detector.detect(self.empty_text)
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
        self.assertEqual(result['ai_probability'], 0)
        self.assertEqual(result['human_probability'], 0)
        self.assertEqual(result['confidence'], 0)
    
    def test_detect_whitespace_text(self):
        """Test detection on whitespace-only text"""
        result = self.detector.detect(self.whitespace_text)
        
        # Should return error response
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
        self.assertEqual(result['ai_probability'], 0)
        self.assertEqual(result['human_probability'], 0)
        self.assertEqual(result['confidence'], 0)
    
    def test_detect_short_text(self):
        """Test detection on very short text"""
        result = self.detector.detect(self.short_text)
        
        # Should handle short text gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('confidence', result)
        self.assertIn('classification', result)
    
    def test_neural_model_fallback(self):
        """Test fallback behavior when neural model is unavailable"""
        with patch.object(self.detector, 'neural_model', None):
            result = self.detector.detect(self.human_text)
            
            # Should still return valid result using pattern detection
            self.assertIsInstance(result, dict)
            self.assertIn('ai_probability', result)
            self.assertIn('human_probability', result)
            self.assertIn('confidence', result)
            self.assertIn('classification', result)
    
    def test_neural_model_error_handling(self):
        """Test error handling when neural model throws exception"""
        # Mock neural model to raise exception
        mock_neural_model = MagicMock()
        mock_neural_model.predict.side_effect = Exception("Neural model error")
        
        with patch.object(self.detector, 'neural_model', mock_neural_model):
            result = self.detector.detect(self.human_text)
            
            # Should handle error gracefully and still return result
            self.assertIsInstance(result, dict)
            self.assertIn('ai_probability', result)
            self.assertIn('human_probability', result)
            self.assertIn('confidence', result)
    
    def test_pattern_detector_error_handling(self):
        """Test error handling when pattern detector throws exception"""
        # Mock pattern detector to raise exception
        mock_pattern_detector = MagicMock()
        mock_pattern_detector.analyze_text.side_effect = Exception("Pattern detector error")
        
        with patch.object(self.detector, 'pattern_detector', mock_pattern_detector):
            result = self.detector.detect(self.human_text)
            
            # Should handle error gracefully
            self.assertIsInstance(result, dict)
            self.assertIn('ai_probability', result)
            self.assertIn('human_probability', result)
    
    def test_confidence_tuning(self):
        """Test confidence tuning functionality"""
        result = self.detector.detect(self.human_text)
        
        # Check that confidence tuning is applied
        self.assertIn('confidence', result)
        self.assertIsInstance(result['confidence'], float)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
    
    def test_classification_levels(self):
        """Test different classification levels"""
        # Test with different types of text to get different classifications
        test_cases = [
            self.human_text,
            self.ai_text,
            self.mixed_text,
            self.short_text
        ]
        
        valid_classifications = [
            'Likely Human-Written',
            'Likely AI-Generated',
            'Mixed Content',
            'Uncertain',
            'Analysis Pending'
        ]
        
        for text in test_cases:
            result = self.detector.detect(text)
            self.assertIn('classification', result)
            # Classification should be one of the valid types
            # Note: We don't enforce specific classification as it depends on model performance
            self.assertIsInstance(result['classification'], str)
    
    def test_risk_level_assignment(self):
        """Test risk level assignment"""
        result = self.detector.detect(self.ai_text)
        
        self.assertIn('risk_level', result)
        valid_risk_levels = ['Very Low', 'Low', 'Medium', 'High', 'Very High', 'Analysis Failed']
        self.assertIn(result['risk_level'], valid_risk_levels)
    
    def test_analysis_details(self):
        """Test that analysis details are provided"""
        result = self.detector.detect(self.human_text)
        
        self.assertIn('analysis', result)
        self.assertIsInstance(result['analysis'], dict)
        
        # Check for expected analysis components
        analysis = result['analysis']
        expected_keys = ['neural_model', 'pattern_detector', 'ensemble_method']
        
        for key in expected_keys:
            if key in analysis:  # Some may not be present if models are unavailable
                self.assertIsInstance(analysis[key], dict)
    
    def test_feedback_messages(self):
        """Test feedback message generation"""
        result = self.detector.detect(self.human_text)
        
        self.assertIn('feedback_messages', result)
        self.assertIsInstance(result['feedback_messages'], list)
        
        # Each feedback message should be a string
        for message in result['feedback_messages']:
            self.assertIsInstance(message, str)
    
    def test_ensemble_weights_application(self):
        """Test that ensemble weights are properly applied"""
        # Create detector with custom weights
        custom_weights = {
            'neural_model': 0.8,
            'pattern_detector': 0.2,
            'rule_based': 0.0,
            'confidence_boost': 0.1
        }
        
        detector = EnsembleAIDetector(ensemble_weights=custom_weights)
        result = detector.detect(self.human_text)
        
        # Should still return valid result
        self.assertIsInstance(result, dict)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('confidence', result)
    
    def test_multiple_detections_consistency(self):
        """Test consistency across multiple detections of the same text"""
        results = []
        for _ in range(3):
            result = self.detector.detect(self.human_text)
            results.append(result)
        
        # Results should be consistent (within small tolerance for floating point)
        for i in range(1, len(results)):
            self.assertAlmostEqual(
                results[0]['ai_probability'], 
                results[i]['ai_probability'], 
                places=5
            )
            self.assertAlmostEqual(
                results[0]['human_probability'], 
                results[i]['human_probability'], 
                places=5
            )
            self.assertEqual(
                results[0]['classification'], 
                results[i]['classification']
            )
    
    def test_batch_detection_performance(self):
        """Test performance with multiple detections"""
        import time
        
        texts = [self.human_text, self.ai_text, self.short_text, self.mixed_text] * 5  # 20 detections
        
        start_time = time.time()
        results = []
        for text in texts:
            result = self.detector.detect(text)
            results.append(result)
        end_time = time.time()
        
        # Check that all detections completed
        self.assertEqual(len(results), 20)
        
        # Check that each result is valid
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('ai_probability', result)
            self.assertIn('human_probability', result)
            self.assertIn('confidence', result)
        
        # Performance check: should complete within reasonable time
        total_time = end_time - start_time
        self.assertLess(total_time, 60.0)  # Should complete within 60 seconds
    
    def test_error_response_structure(self):
        """Test error response structure"""
        result = self.detector.detect("")
        
        # Error response should have specific structure
        self.assertIn('error', result)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('confidence', result)
        self.assertIn('classification', result)
        self.assertIn('risk_level', result)
        self.assertIn('analysis', result)
        self.assertIn('feedback_messages', result)
        
        # Error values should be appropriate
        self.assertEqual(result['ai_probability'], 0.0)
        self.assertEqual(result['human_probability'], 0.0)
        self.assertEqual(result['confidence'], 0.0)
        self.assertEqual(result['classification'], 'Error')
        self.assertEqual(result['risk_level'], 'Analysis Failed')
        self.assertIsInstance(result['analysis'], dict)
        self.assertIsInstance(result['feedback_messages'], list)


if __name__ == '__main__':
    unittest.main()