#!/usr/bin/env python3
"""
Simple API test for content detection endpoint
"""

import requests
import json

def test_api_endpoint():
    """Test the content detection API endpoint"""
    
    # Test data
    test_cases = [
        {
            "text": "Hey! I just got back from the most amazing trip to Japan. The food was incredible!",
            "expected": "human"
        },
        {
            "text": "Urban green spaces play a crucial role in enhancing the quality of life in modern cities. Furthermore, these areas contribute significantly to environmental sustainability.",
            "expected": "ai"
        }
    ]
    
    base_url = "http://localhost:5001"
    endpoint = f"{base_url}/api/detect"
    
    print("🧪 Testing AI Content Detection API")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['expected'].upper()} text")
        print(f"Text: {test_case['text'][:60]}...")
        
        try:
            # Make API request
            response = requests.post(
                endpoint,
                json={"text": test_case["text"]},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {response.status_code}")
                
                ai_prob = result.get('ai_probability', 'N/A')
                confidence = result.get('confidence', 'N/A')
                
                if isinstance(ai_prob, (int, float)):
                    print(f"🎯 AI Probability: {ai_prob:.1%}")
                else:
                    print(f"🎯 AI Probability: {ai_prob}")
                    
                if isinstance(confidence, (int, float)):
                    print(f"📊 Confidence: {confidence:.1%}")
                else:
                    print(f"📊 Confidence: {confidence}")
                    
                print(f"🏷️  Classification: {result.get('classification', 'N/A')}")
                print(f"🔧 Method: {result.get('method', 'N/A')}")
                print(f"📋 Full Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Backend server not running on port 5001")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 API test completed!")

if __name__ == "__main__":
    test_api_endpoint()