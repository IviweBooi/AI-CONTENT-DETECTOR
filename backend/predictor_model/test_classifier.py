#!/usr/bin/env python3
"""
Simple test script for the AI text classifier
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_text_classifier import AITextClassifier

def test_classifier():
    """Test the AI text classifier with sample texts"""
    print("Testing AI Text Classifier...")
    
    try:
        # Initialize the classifier
        classifier = AITextClassifier()
        print("✓ Classifier initialized successfully")
        
        # Test with sample texts
        test_texts = [
            "This is a simple human-written text about everyday life.",
            "Furthermore, the comprehensive analysis demonstrates that the aforementioned methodology provides substantial evidence for the hypothesis, consequently leading to the conclusion that the implementation of such strategies would be beneficial for organizational efficiency.",
            "I went to the store today and bought some groceries. The weather was nice."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n--- Test {i} ---")
            print(f"Text: {text[:50]}...")
            
            result = classifier.predict(text)
            print(f"Prediction: {result['prediction']}")
            print(f"AI Probability: {result['ai_probability']:.2f}")
            print(f"Human Probability: {result['human_probability']:.2f}")
            print(f"Confidence: {result['confidence']:.2f}")
            
            if 'error' in result:
                print(f"Error: {result['error']}")
        
        print("\n✓ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_classifier()
    sys.exit(0 if success else 1)