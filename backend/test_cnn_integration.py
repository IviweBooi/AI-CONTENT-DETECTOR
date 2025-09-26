#!/usr/bin/env python3
"""
Test script for CNN model integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from predictor_model.cnn_text_classifier import CNNTextClassifier

def test_cnn_model():
    """Test the CNN model integration"""
    print("Testing CNN Model Integration...")
    print("=" * 50)
    
    # Initialize the CNN classifier
    try:
        cnn_classifier = CNNTextClassifier()
        print("✓ CNN Classifier initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize CNN Classifier: {e}")
        return False
    
    # Test sample texts
    test_texts = [
        "This is a human-written text with natural flow and personal expression.",
        "The implementation of artificial intelligence systems requires careful consideration of various factors including data preprocessing, model architecture, and evaluation metrics.",
        "I love spending time with my family and friends during the weekends.",
        "Machine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning paradigms."
    ]
    
    print("\nTesting predictions:")
    print("-" * 30)
    
    for i, text in enumerate(test_texts, 1):
        try:
            result = cnn_classifier.predict(text)
            print(f"\nTest {i}:")
            print(f"Text: {text[:60]}...")
            print(f"Prediction: {result['prediction']}")
            print(f"Confidence: {result['confidence']:.4f}")
            print(f"AI Probability: {result['ai_probability']:.4f}")
            print(f"Human Probability: {result['human_probability']:.4f}")
        except Exception as e:
            print(f"✗ Error predicting text {i}: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("✓ CNN Model Integration Test Completed Successfully!")
    return True

if __name__ == "__main__":
    success = test_cnn_model()
    if success:
        print("\n🎉 All tests passed! CNN model is ready for integration.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")