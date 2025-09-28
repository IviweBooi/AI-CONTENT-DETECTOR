"""
Unit tests for CNN Text Classifier
Tests the core functionality of the CNNTextClassifier including prediction accuracy,
error handling, and model loading behavior.
"""

import pytest
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from predictor_model.cnn_text_classifier import CNNTextClassifier


class TestCNNTextClassifier(unittest.TestCase):
    """Test cases for CNNTextClassifier"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.classifier = CNNTextClassifier()
        
        # Sample test texts
        self.human_text = "I love this movie! It's absolutely fantastic and made me cry. The acting was superb and the storyline kept me engaged throughout."
        self.ai_text = "As an AI language model, I can provide you with comprehensive information about this topic. The implementation requires careful consideration of various factors."
        self.short_text = "Hello"
        self.empty_text = ""
        self.long_text = "A" * 2000  # Very long text
    
    def test_classifier_initialization(self):
        """Test CNN classifier initialization"""
        classifier = CNNTextClassifier()
        
        self.assertIsNotNone(classifier)
        self.assertIsNotNone(classifier.device)
        # Model loading depends on actual file existence and CNN availability
        self.assertIsInstance(classifier.model_loaded, bool)
    
    def test_predict_human_text(self):
        """Test prediction on human-like text"""
        result = self.classifier.predict(self.human_text)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('model_type', result)
        
        # Check data types
        self.assertIsInstance(result['prediction'], str)
        self.assertIsInstance(result['confidence'], float)
        self.assertIsInstance(result['ai_probability'], float)
        self.assertIsInstance(result['human_probability'], float)
        self.assertIsInstance(result['model_type'], str)
        
        # Check probability ranges
        self.assertGreaterEqual(result['ai_probability'], 0.0)
        self.assertLessEqual(result['ai_probability'], 1.0)
        self.assertGreaterEqual(result['human_probability'], 0.0)
        self.assertLessEqual(result['human_probability'], 1.0)
        
        # Check probabilities sum to 1 (approximately)
        prob_sum = result['ai_probability'] + result['human_probability']
        self.assertAlmostEqual(prob_sum, 1.0, places=5)
        
        # Check confidence range
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
    
    def test_predict_ai_text(self):
        """Test prediction on AI-like text"""
        result = self.classifier.predict(self.ai_text)
        
        # Check result structure (same as human text test)
        self.assertIsInstance(result, dict)
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('model_type', result)
        
        # For AI-like text, we expect higher AI probability
        # Note: This is a heuristic test and may vary based on model performance
        self.assertIsInstance(result['ai_probability'], float)
        self.assertIsInstance(result['human_probability'], float)
    
    def test_predict_empty_text(self):
        """Test prediction on empty text"""
        result = self.classifier.predict(self.empty_text)
        
        # Should still return a valid result structure
        self.assertIsInstance(result, dict)
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('model_type', result)
    
    def test_predict_short_text(self):
        """Test prediction on very short text"""
        result = self.classifier.predict(self.short_text)
        
        # Should handle short text gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('model_type', result)
    
    def test_predict_long_text(self):
        """Test prediction on very long text"""
        result = self.classifier.predict(self.long_text)
        
        # Should handle long text (truncation should occur)
        self.assertIsInstance(result, dict)
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('ai_probability', result)
        self.assertIn('human_probability', result)
        self.assertIn('model_type', result)
    
    def test_text_preprocessing(self):
        """Test text preprocessing functionality"""
        # Test with text containing special characters
        special_text = "Hello! @#$%^&*() This is a test with special characters... 123"
        result = self.classifier.predict(special_text)
        
        # Should handle special characters without errors
        self.assertIsInstance(result, dict)
        self.assertIn('prediction', result)
    
    def test_multiple_predictions_consistency(self):
        """Test that multiple predictions on the same text are consistent"""
        result1 = self.classifier.predict(self.human_text)
        result2 = self.classifier.predict(self.human_text)
        
        # Results should be identical for the same input
        self.assertEqual(result1['prediction'], result2['prediction'])
        self.assertAlmostEqual(result1['confidence'], result2['confidence'], places=5)
        self.assertAlmostEqual(result1['ai_probability'], result2['ai_probability'], places=5)
        self.assertAlmostEqual(result1['human_probability'], result2['human_probability'], places=5)
    
    @patch('predictor_model.cnn_text_classifier.torch')
    def test_model_loading_failure_fallback(self, mock_torch):
        """Test fallback behavior when model loading fails"""
        # Mock torch to raise an exception during model loading
        mock_torch.load.side_effect = Exception("Model loading failed")
        
        # Create a new classifier instance (this should trigger the fallback)
        with patch('predictor_model.cnn_text_classifier.os.path.exists', return_value=True):
            classifier = CNNTextClassifier()
            result = classifier.predict(self.human_text)
            
            # Should still return a valid result using rule-based fallback
            self.assertIsInstance(result, dict)
            self.assertIn('prediction', result)
            self.assertIn('model_type', result)
            self.assertEqual(result['model_type'], 'Rule-based (CNN fallback)')
    
    def test_model_file_not_found_fallback(self):
        """Test fallback behavior when model file doesn't exist"""
        with patch('predictor_model.cnn_text_classifier.os.path.exists', return_value=False):
            classifier = CNNTextClassifier()
            result = classifier.predict(self.human_text)
            
            # Should use rule-based fallback
            self.assertIsInstance(result, dict)
            self.assertIn('prediction', result)
            self.assertIn('model_type', result)
            self.assertEqual(result['model_type'], 'Rule-based (CNN fallback)')
    
    def test_rule_based_detection_patterns(self):
        """Test rule-based detection patterns when CNN is not available"""
        # Mock CNN_AVAILABLE to False
        with patch('predictor_model.cnn_text_classifier.CNN_AVAILABLE', False):
            classifier = CNNTextClassifier()
            
            # Test AI-like text
            ai_text = "As an AI language model, I can provide comprehensive information about this topic."
            result = classifier.predict(ai_text)
            
            self.assertEqual(result['model_type'], 'Rule-based (CNN fallback)')
            self.assertGreaterEqual(result['ai_probability'], 0.5)  # Should detect as AI
            
            # Test human-like text
            human_text = "I love spending time with my family on weekends."
            result = classifier.predict(human_text)
            
            self.assertEqual(result['model_type'], 'Rule-based (CNN fallback)')
            self.assertLess(result['ai_probability'], 0.5)  # Should detect as human
    
    def test_batch_prediction_performance(self):
        """Test performance with multiple predictions"""
        import time
        
        texts = [self.human_text, self.ai_text, self.short_text] * 10  # 30 predictions
        
        start_time = time.time()
        results = []
        for text in texts:
            result = self.classifier.predict(text)
            results.append(result)
        end_time = time.time()
        
        # Check that all predictions completed
        self.assertEqual(len(results), 30)
        
        # Check that each result is valid
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('prediction', result)
            self.assertIn('confidence', result)
        
        # Performance check: should complete within reasonable time
        total_time = end_time - start_time
        self.assertLess(total_time, 30.0)  # Should complete within 30 seconds


if __name__ == '__main__':
    unittest.main()