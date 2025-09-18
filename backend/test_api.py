#!/usr/bin/env python3
"""
Test script to verify the API endpoints work with temporary file processing.
"""

import requests
import json

def test_content_detection():
    """Test the content detection endpoint."""
    print("🔍 Testing Content Detection API...")
    print("=" * 50)
    
    url = "http://localhost:5001/api/detect"
    
    try:
        # Test with the text file
        with open('test_content.txt', 'rb') as f:
            files = {'file': ('test_content.txt', f, 'text/plain')}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Content detection successful!")
            print(f"📄 File processed: {result.get('filename', 'N/A')}")
            print(f"📝 Text length: {result.get('text_length', 'N/A')}")
            
            analysis = result.get('analysis_result', {})
            if analysis:
                print(f"🤖 AI Probability: {analysis.get('ai_probability', 'N/A')}")
                print(f"🎯 Confidence: {analysis.get('confidence', 'N/A')}")
                print(f"📊 Classification: {analysis.get('classification', 'N/A')}")
            
            # Check if storage info is NOT included (as expected)
            if 'storage_info' not in result:
                print("✅ Storage info correctly excluded (temporary processing)")
            else:
                print("⚠️  Storage info found (unexpected)")
            
            # Check if processing info is included
            if 'processing_info' in result:
                print("✅ Processing info included (temporary mode)")
                print(f"   Mode: {result['processing_info'].get('mode', 'N/A')}")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Is it running on port 5001?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_check():
    """Test the health check endpoint."""
    print("\n🏥 Testing Health Check API...")
    print("=" * 50)
    
    url = "http://localhost:5001/api/health"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check successful!")
            print(f"📊 Status: {result.get('status', 'N/A')}")
            
            services = result.get('services', {})
            for service, status in services.items():
                print(f"   {service}: {status}")
                
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_health_check()
    test_content_detection()
    print("\n🎉 API testing completed!")