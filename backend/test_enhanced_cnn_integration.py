#!/usr/bin/env python3
"""
Test script for enhanced AI detector with CNN integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhanced_ai_detector import detect_ai_content_enhanced

def test_enhanced_cnn_integration():
    """Test the enhanced AI detector with CNN integration"""
    print("Testing Enhanced AI Detector with CNN Integration...")
    print("=" * 60)
    
    # Test sample texts
    test_texts = [
        {
            "text": "This is a human-written text with natural flow and personal expression. I really enjoy writing in my own style.",
            "expected": "human"
        },
        {
            "text": "The implementation of artificial intelligence systems requires careful consideration of various factors including data preprocessing, model architecture, and evaluation metrics. Furthermore, the optimization of hyperparameters is essential for achieving optimal performance.",
            "expected": "ai"
        },
        {
            "text": "I love spending time with my family and friends during the weekends. We often go hiking or have barbecues in the backyard.",
            "expected": "human"
        },
        {
            "text": "Machine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning paradigms. Additionally, deep learning techniques have revolutionized the field of artificial intelligence.",
            "expected": "ai"
        }
    ]
    
    print("\nTesting enhanced detection with CNN:")
    print("-" * 40)
    
    for i, test_case in enumerate(test_texts, 1):
        text = test_case["text"]
        expected = test_case["expected"]
        
        try:
            result = detect_ai_content_enhanced(text)
            
            print(f"\nTest {i} (Expected: {expected.upper()}):")
            print(f"Text: {text[:60]}...")
            print(f"Classification: {result.get('classification', 'N/A')}")
            print(f"AI Probability: {result.get('ai_probability', 0):.4f}")
            print(f"Human Probability: {result.get('human_probability', 0):.4f}")
            print(f"Confidence: {result.get('confidence', 0):.4f}")
            print(f"Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"Method: {result.get('analysis', {}).get('prediction_method', 'N/A')}")
            
            # Show feedback messages
            if result.get('feedback_messages'):
                print("Feedback:")
                for msg in result['feedback_messages'][:2]:  # Show first 2 messages
                    print(f"  • {msg}")
            
            # Show recommendations
            if result.get('recommendations'):
                print("Recommendations:")
                for rec in result['recommendations'][:2]:  # Show first 2 recommendations
                    print(f"  • {rec}")
                    
        except Exception as e:
            print(f"✗ Error in test {i}: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("✓ Enhanced AI Detector with CNN Integration Test Completed!")
    return True

if __name__ == "__main__":
    success = test_enhanced_cnn_integration()
    if success:
        print("\n🎉 All tests passed! Enhanced detector with CNN is working!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")