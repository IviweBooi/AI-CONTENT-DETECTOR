#!/usr/bin/env python3
"""
Test script to verify enhanced pattern detection through the live API
"""

import requests
import json

def test_api_with_patterns():
    api_url = "http://localhost:5001/api/detect"
    
    # Test cases with different patterns
    test_cases = [
        {
            "name": "Excessive Em-dashes (AI Pattern)",
            "text": "The implementation of AI systems — particularly in healthcare — has shown remarkable results. These technologies — when properly deployed — can enhance diagnostic accuracy. Furthermore — and this is crucial — the integration must be seamless to ensure optimal outcomes."
        },
        {
            "name": "Human Conversational Text",
            "text": "I can't believe how much technology has changed our lives! It's pretty amazing when you think about it. My grandmother always says she never imagined we'd have computers in our pockets. But here we are, and honestly? I think we're just getting started."
        },
        {
            "name": "AI Buzzword Heavy Text",
            "text": "Furthermore, it is important to note that artificial intelligence has revolutionized numerous industries. Moreover, the cutting-edge technology continues to evolve at an unprecedented pace. Additionally, organizations must leverage these innovative solutions to optimize their operations."
        },
        {
            "name": "Human Literary Text (Dickens)",
            "text": "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness."
        }
    ]
    
    for test_case in test_cases:
        print(f"\n=== {test_case['name']} ===")
        
        try:
            response = requests.post(api_url, json={"text": test_case["text"]})
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', data)  # Handle nested structure
                print(f"AI Probability: {result['ai_probability']:.3f}")
                print(f"Classification: {result['classification']}")
                print(f"Confidence: {result['confidence']:.3f}")
                print(f"Detection Method: {result.get('detection_method', 'unknown')}")
                
                # Check if pattern analysis is included
                if 'pattern_analysis' in result:
                    patterns = result['pattern_analysis']['patterns_detected']
                    print(f"Patterns detected: {len(patterns)}")
                    for pattern in patterns[:3]:  # Show first 3 patterns
                        print(f"  - {pattern['description']} (strength: {pattern['strength']:.2f})")
                else:
                    print("No pattern analysis found in response")
                
                # Show feedback messages
                if 'feedback_messages' in result:
                    print("Feedback:")
                    for msg in result['feedback_messages'][:2]:  # Show first 2 messages
                        print(f"  - {msg}")
                        
            else:
                print(f"API Error: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to API. Make sure the backend server is running on localhost:5001")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_api_with_patterns()