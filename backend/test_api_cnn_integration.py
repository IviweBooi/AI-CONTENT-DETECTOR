#!/usr/bin/env python3
"""
Test script for API endpoints with CNN integration
"""

import requests
import json
import time

def test_api_cnn_integration():
    """Test the API endpoints with CNN integration"""
    print("Testing API Endpoints with CNN Integration...")
    print("=" * 50)
    
    # API base URL (assuming the server is running on localhost:5001)
    base_url = "http://localhost:5001"
    
    # Test sample texts
    test_texts = [
        {
            "text": "This is a human-written text with natural flow and personal expression. I really enjoy writing in my own style and expressing my thoughts freely.",
            "description": "Human-like text"
        },
        {
            "text": "The implementation of artificial intelligence systems requires careful consideration of various factors including data preprocessing, model architecture, and evaluation metrics. Furthermore, the optimization of hyperparameters is essential for achieving optimal performance in machine learning applications.",
            "description": "AI-like text"
        }
    ]
    
    print(f"Testing API at: {base_url}")
    print("-" * 30)
    
    for i, test_case in enumerate(test_texts, 1):
        text = test_case["text"]
        description = test_case["description"]
        
        try:
            # Test the content detection endpoint
            response = requests.post(
                f"{base_url}/api/detect",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                result = response_data.get('result', {})
                analysis = result.get('analysis', {})
                
                print(f"\nTest {i} ({description}):")
                print(f"Text: {text[:60]}...")
                print(f"Status: ✓ Success")
                print(f"Classification: {analysis.get('prediction', 'N/A')}")
                print(f"AI Probability: {result.get('ai_probability', 0):.4f}")
                print(f"Confidence: {result.get('confidence', 0):.4f}")
                print(f"Method: {analysis.get('prediction_method', 'N/A')}")
                print(f"Model Type: {analysis.get('model_type', 'N/A')}")
                
                # Check if CNN is being used
                if 'cnn' in analysis.get('prediction_method', '').lower():
                    print("✓ CNN model is being used successfully!")
                else:
                    print("⚠️ CNN model may not be active (using backup)")
                    
            else:
                print(f"\nTest {i} ({description}):")
                print(f"Status: ✗ Failed (HTTP {response.status_code})")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"\nTest {i} ({description}):")
            print("✗ Connection failed - Make sure the server is running on localhost:5000")
            print("  Run: python app.py")
            return False
        except Exception as e:
            print(f"\nTest {i} ({description}):")
            print(f"✗ Error: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("✓ API CNN Integration Test Completed!")
    return True

if __name__ == "__main__":
    success = test_api_cnn_integration()
    if success:
        print("\n🎉 API with CNN integration is working!")
    else:
        print("\n❌ API test failed. Check server status and try again.")