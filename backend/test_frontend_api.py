#!/usr/bin/env python3
"""
Test script to simulate frontend API calls and debug the data flow
"""

import requests
import json

def test_frontend_api():
    """Test the API endpoint that the frontend uses"""
    
    # Test with human-written text
    human_text = "This is a simple human-written sentence about the weather today. The sun is shining brightly and there are a few clouds in the sky."
    
    print("🔍 Testing Frontend API Endpoint")
    print("=" * 50)
    
    try:
        # Make the same API call that the frontend makes
        response = requests.post(
            'http://localhost:5001/api/detect',
            headers={'Content-Type': 'application/json'},
            json={'text': human_text}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🔍 Raw Backend Response:")
            print(json.dumps(result, indent=2))
            
            print(f"\n🔍 Frontend Data Processing:")
            print(f"result.success: {result.get('success')}")
            print(f"result.result: {result.get('result')}")
            
            if result.get('result'):
                backend_data = result['result']
                print(f"\n🔍 Backend Data Structure:")
                print(f"ai_probability: {backend_data.get('ai_probability')}")
                print(f"human_probability: {backend_data.get('human_probability')}")
                print(f"classification: {backend_data.get('classification')}")
                print(f"confidence: {backend_data.get('confidence')}")
                
                # Simulate frontend display calculation
                ai_prob = backend_data.get('ai_probability', 0)
                display_percentage = round(ai_prob * 100)
                print(f"\n🔍 Frontend Display Calculation:")
                print(f"AI Probability: {ai_prob}")
                print(f"Display Percentage: {display_percentage}%")
                print(f"Classification: {backend_data.get('classification', 'Likely AI-generated' if ai_prob >= 0.51 else 'Likely human-written')}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error making API call: {e}")

if __name__ == "__main__":
    test_frontend_api()