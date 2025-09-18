#!/usr/bin/env python3
"""
Simple test script to verify API endpoints are working
"""
import requests
import json

def test_endpoints():
    base_url = "http://localhost:5001/api"
    
    print("🔍 Testing API endpoints...")
    
    # Test health endpoint
    try:
        print("\n1. Testing /health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test export-formats endpoint
    try:
        print("\n2. Testing /export-formats endpoint...")
        response = requests.get(f"{base_url}/export-formats")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test text detection
    try:
        print("\n3. Testing /detect endpoint with text...")
        test_text = "This is a sample text for AI detection testing."
        response = requests.post(f"{base_url}/detect", 
                               json={"text": test_text},
                               headers={"Content-Type": "application/json"})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
            if result.get('success'):
                print(f"   AI Probability: {result.get('result', {}).get('ai_probability', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Endpoint testing completed!")

if __name__ == "__main__":
    test_endpoints()