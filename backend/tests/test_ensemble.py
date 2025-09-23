#!/usr/bin/env python3
"""
Test script for the neural AI detector to verify detection accuracy.
"""

import sys
import os

# Add parent directory to path to access utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.neural_detector import NeuralAIDetector
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the utils modules are available")
    # Don't exit during pytest execution
    import pytest
    pytest.skip(f"Skipping test due to import error: {e}", allow_module_level=True)

def test_neural_detector():
    """Test the neural detector with AI-generated sample text."""
    
    # Read the AI sample text
    sample_file = os.path.join(os.path.dirname(__file__), 'ai_sample_text.txt')
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_text = f.read().strip()
    except FileNotFoundError:
        print(f"Sample file not found: {sample_file}")
        return
    
    print("Testing Neural AI Detector")
    print("=" * 50)
    print(f"Text length: {len(sample_text)} characters")
    print(f"Sample text preview: {sample_text[:200]}...")
    print("=" * 50)
    
    # Test neural detector
    print("\n1. Neural Detection (RoBERTa Model):")
    print("-" * 35)
    neural_detector = NeuralAIDetector()
    neural_result = neural_detector.detect(sample_text)
    
    print(f"AI Probability: {neural_result['ai_probability']:.1%}")
    print(f"Human Probability: {neural_result['human_probability']:.1%}")
    print(f"Confidence: {neural_result['confidence']:.1%}")
    print(f"Classification: {neural_result['classification']}")
    print(f"Risk Level: {neural_result['risk_level']}")
    
    if 'method_info' in neural_result:
        method_info = neural_result['method_info']
        print(f"Detection Method: {method_info.get('method', 'unknown')}")
        if 'neural_prediction' in method_info and method_info['neural_prediction'] is not None:
            print(f"Neural Prediction: {method_info['neural_prediction']:.1%}")
    
    print("\nFeedback Messages:")
    for msg in neural_result.get('feedback_messages', [])[:5]:
        print(f"  • {msg}")
    
    print("\n" + "=" * 50)
    print("Neural Detection Summary:")
    print(f"AI Probability: {neural_result['ai_probability']:.1%}")
    print(f"Confidence: {neural_result['confidence']:.1%}")
    print(f"Classification: {neural_result['classification']}")
    
    # Determine detection quality
    if neural_result['ai_probability'] >= 0.8:
        print("✅ High confidence AI detection")
    elif neural_result['ai_probability'] >= 0.6:
        print("⚡ Moderate AI probability detected")
    elif neural_result['ai_probability'] >= 0.4:
        print("🤔 Uncertain classification")
    else:
        print("👤 Likely human-written content")
    
def test_neural_functionality():
    """Pytest function to test neural detector functionality."""
    try:
        detector = NeuralAIDetector()
        sample_text = "This is a test text for AI detection."
        result = detector.detect(sample_text)
        
        # Basic assertions
        assert 'ai_probability' in result
        assert 'human_probability' in result
        assert 'confidence' in result
        assert 'classification' in result
        assert 'risk_level' in result
        
        # Probability assertions
        assert 0 <= result['ai_probability'] <= 1
        assert 0 <= result['human_probability'] <= 1
        assert abs(result['ai_probability'] + result['human_probability'] - 1.0) < 0.01
        
        print("✅ All neural detector tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_neural_detector()