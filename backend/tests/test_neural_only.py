#!/usr/bin/env python3
"""
Test script to verify neural-only AI detection system
"""

import sys
import os
# Add parent directory to path to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhanced_ai_detector import detect_ai_content_enhanced

def test_neural_only_detection():
    """Test the neural-only AI detection system"""
    
    test_texts = [
        {
            "name": "Human-like casual text",
            "text": "Hey! I just got back from the most amazing trip to Japan. The food was incredible, especially this little ramen shop I found in Tokyo. Can't wait to go back!"
        },
        {
            "name": "AI-like formal text", 
            "text": "Urban green spaces play a crucial role in enhancing the quality of life in modern cities. Furthermore, they provide essential environmental benefits including air purification and temperature regulation."
        },
        {
            "name": "Technical content",
            "text": "The implementation of machine learning algorithms requires careful consideration of data preprocessing, feature engineering, and model validation techniques to ensure optimal performance."
        },
        {
            "name": "Creative writing",
            "text": "The old lighthouse stood defiantly against the crashing waves, its beacon cutting through the fog like a sword through silk. Sarah pulled her coat tighter as she approached."
        }
    ]
    
    print("🧪 Testing Neural-Only AI Detection System")
    print("=" * 50)
    
    for i, test_case in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Text: {test_case['text'][:100]}...")
        
        try:
            result = detect_ai_content_enhanced(test_case['text'])
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue
                
            ai_prob = result.get('ai_probability', 0)
            confidence = result.get('confidence', 0)
            classification = result.get('classification', 'Unknown')
            method = result.get('analysis', {}).get('prediction_method', 'unknown')
            
            print(f"🎯 AI Probability: {ai_prob:.1%}")
            print(f"📊 Confidence: {confidence:.1%}")
            print(f"🏷️  Classification: {classification}")
            print(f"🔧 Method: {method}")
            
            # Verify it's using neural-only method
            if method == 'neural_only':
                print("✅ Using neural-only detection (correct)")
            else:
                print(f"⚠️  Expected neural-only, got: {method}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Neural-only detection test completed!")

if __name__ == "__main__":
    test_neural_only_detection()