#!/usr/bin/env python3
"""
Comprehensive test script demonstrating enhanced AI detection capabilities
with pattern recognition for AI-specific markers like em-dashes and human writing styles.
"""

import requests
import json

def test_enhanced_ai_detection():
    """Test the enhanced AI detection with various pattern-based examples"""
    api_url = "http://localhost:5001/api/detect"
    
    print("🔍 Enhanced AI Detection Test Suite")
    print("=" * 60)
    
    # Test cases demonstrating different AI and human patterns
    test_cases = [
        {
            "name": "🤖 AI Pattern: Excessive Em-dashes",
            "text": "The implementation of AI systems — particularly in healthcare — has shown remarkable results. These technologies — when properly deployed — can enhance diagnostic accuracy. Furthermore — and this is crucial — the integration must be seamless to ensure optimal outcomes.",
            "expected": "AI-Generated",
            "pattern": "Em-dashes overuse"
        },
        {
            "name": "🤖 AI Pattern: Buzzword Heavy",
            "text": "Furthermore, it is important to note that artificial intelligence has revolutionized numerous industries. Moreover, the cutting-edge technology continues to evolve at an unprecedented pace. Additionally, organizations must leverage these innovative solutions to optimize their operations and streamline their processes.",
            "expected": "AI-Generated", 
            "pattern": "AI buzzwords and formal transitions"
        },
        {
            "name": "👤 Human Pattern: Conversational Style",
            "text": "I can't believe how much technology has changed our lives! It's pretty amazing when you think about it. My grandmother always says she never imagined we'd have computers in our pockets. But here we are, and honestly? I think we're just getting started.",
            "expected": "Human-Written",
            "pattern": "Contractions, personal voice, informal language"
        },
        {
            "name": "👤 Human Pattern: Literary Classic",
            "text": "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness.",
            "expected": "Human-Written",
            "pattern": "Literary style, repetitive structure"
        },
        {
            "name": "🤖 AI Pattern: Uniform Sentences",
            "text": "Machine learning algorithms are transforming business operations. Data analytics provides valuable insights for decision making. Artificial intelligence enhances productivity across various sectors. Technology integration improves organizational efficiency significantly.",
            "expected": "AI-Generated",
            "pattern": "Uniform sentence length and structure"
        },
        {
            "name": "👤 Human Pattern: Emotional Expression",
            "text": "Wow! This is absolutely incredible. I'm so excited about this new discovery. It's mind-blowing how far we've come. Can you believe it? This changes everything! I'm literally speechless right now.",
            "expected": "Human-Written",
            "pattern": "Emotional language, exclamations, varied punctuation"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Pattern: {test_case['pattern']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            response = requests.post(api_url, json={"text": test_case["text"]})
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', data)
                
                ai_prob = result['ai_probability']
                classification = result['classification']
                confidence = result['confidence']
                
                # Determine if prediction matches expectation
                is_correct = (
                    ("AI-Generated" in classification and "AI-Generated" in test_case['expected']) or
                    ("Human-Written" in classification and "Human-Written" in test_case['expected'])
                )
                
                status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
                
                print(f"   Result: {classification} ({ai_prob:.1%} AI)")
                print(f"   Confidence: {confidence:.1%}")
                print(f"   Status: {status}")
                
                # Show detected patterns
                if 'pattern_analysis' in result:
                    patterns = result['pattern_analysis']['patterns_detected']
                    if patterns:
                        print(f"   Patterns detected ({len(patterns)}):")
                        for pattern in patterns[:3]:  # Show top 3 patterns
                            print(f"     • {pattern['description']}")
                
                results.append({
                    'name': test_case['name'],
                    'correct': is_correct,
                    'ai_probability': ai_prob,
                    'classification': classification,
                    'confidence': confidence
                })
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                results.append({'name': test_case['name'], 'correct': False, 'error': True})
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({'name': test_case['name'], 'correct': False, 'error': True})
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ENHANCED DETECTION SUMMARY")
    print("=" * 60)
    
    correct_count = sum(1 for r in results if r.get('correct', False))
    total_count = len([r for r in results if not r.get('error', False)])
    
    if total_count > 0:
        accuracy = (correct_count / total_count) * 100
        print(f"Accuracy: {correct_count}/{total_count} ({accuracy:.1f}%)")
        
        # Show pattern detection capabilities
        print(f"\n🎯 Pattern Detection Capabilities Demonstrated:")
        print(f"   • Em-dash overuse detection")
        print(f"   • AI buzzword identification") 
        print(f"   • Human conversational style recognition")
        print(f"   • Literary writing pattern detection")
        print(f"   • Sentence uniformity analysis")
        print(f"   • Emotional expression recognition")
        
        if accuracy >= 80:
            print(f"\n🎉 EXCELLENT: Enhanced detection is working well!")
        elif accuracy >= 60:
            print(f"\n👍 GOOD: Enhanced detection shows improvement!")
        else:
            print(f"\n⚠️  NEEDS IMPROVEMENT: Consider adjusting pattern weights")
    else:
        print("❌ No successful tests completed")

if __name__ == "__main__":
    test_enhanced_ai_detection()