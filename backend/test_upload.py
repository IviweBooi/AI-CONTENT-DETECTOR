#!/usr/bin/env python3
"""
Test script to verify file upload functionality
"""
import requests
import json

def test_file_upload():
    """Test the file upload endpoint"""
    url = "http://localhost:5001/api/detect"
    
    # Test with the sample text file
    try:
        with open("test_sample.txt", "rb") as f:
            files = {"file": ("test_sample.txt", f, "text/plain")}
            response = requests.post(url, files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            print(f"Content extracted: {len(data.get('content', ''))} characters")
            print(f"First 100 chars: {data.get('content', '')[:100]}...")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    test_file_upload()